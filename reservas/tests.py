from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from catalogo.models import Vuelo
from cuentas.validators import calcular_dv


class CarpetaSesionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("poblar_datos", verbosity=0)

    def test_agregar_respeta_cupos(self):
        # LA601 tiene 5 cupos
        self.client.post(reverse("reservas:agregar", args=["LA601"]), {"pasajeros": 9})
        self.assertEqual(self.client.session.get("carpeta_reserva", {}), {})
        self.client.post(reverse("reservas:agregar", args=["LA601"]), {"pasajeros": 5})
        self.assertEqual(self.client.session["carpeta_reserva"], {"LA601": 5})

    def test_no_se_agrega_vuelo_cancelado(self):
        self.client.post(reverse("reservas:agregar", args=["H2777"]), {"pasajeros": 1})
        self.assertEqual(self.client.session.get("carpeta_reserva", {}), {})

    def test_calculo_total_con_tasa_e_iva(self):
        self.client.post(reverse("reservas:agregar", args=["JA402"]), {"pasajeros": 2})  # 47.000 x 2
        r = self.client.get(reverse("reservas:carpeta"))
        self.assertEqual(r.context["subtotal"], 94000)
        self.assertEqual(r.context["tasa_embarque"], 17000)
        self.assertEqual(r.context["iva"], 21090)       # 19% de 111.000
        self.assertEqual(r.context["total"], 132090)

    def test_modificar_quitar_y_vaciar(self):
        self.client.post(reverse("reservas:agregar", args=["JA402"]), {"pasajeros": 1})
        self.client.post(reverse("reservas:agregar", args=["LA800"]), {"pasajeros": 1})
        self.client.post(reverse("reservas:modificar", args=["JA402"]), {"pasajeros": 3})
        self.assertEqual(self.client.session["carpeta_reserva"]["JA402"], 3)
        self.client.post(reverse("reservas:quitar", args=["LA800"]))
        self.assertNotIn("LA800", self.client.session["carpeta_reserva"])
        self.client.post(reverse("reservas:vaciar"))
        self.assertEqual(self.client.session.get("carpeta_reserva", {}), {})

    def test_contador_en_navbar(self):
        self.client.post(reverse("reservas:agregar", args=["JA402"]), {"pasajeros": 1})
        r = self.client.get(reverse("catalogo:lista"))
        self.assertEqual(r.context["carpeta_count"], 1)

    def test_confirmar_requiere_login_y_vacia_sesion(self):
        self.client.post(reverse("reservas:agregar", args=["JA402"]), {"pasajeros": 1})
        r = self.client.post(reverse("reservas:confirmar"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/cuentas/login/", r.url)
        self.client.login(username="usuario", password="Usuario12345!")
        r = self.client.post(reverse("reservas:confirmar"))
        self.assertRedirects(r, reverse("reservas:comprobante"))
        self.assertEqual(self.client.session.get("carpeta_reserva", {}), {})
        self.assertContains(self.client.get(reverse("reservas:comprobante")), "CMP-")


class SeguridadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("poblar_datos", verbosity=0)

    def test_gestion_protegida(self):
        url = reverse("catalogo:gestion")
        self.assertEqual(self.client.get(url).status_code, 302)           # anónimo -> login
        self.client.login(username="usuario", password="Usuario12345!")
        r = self.client.get(url)                                           # no staff -> acceso denegado
        self.assertEqual(r.status_code, 302)
        self.assertIn("acceso-denegado", r.url)
        self.client.login(username="admin", password="Admin12345!")
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_crud_baja_logica(self):
        self.client.login(username="admin", password="Admin12345!")
        self.client.post(reverse("catalogo:eliminar", args=["LA800"]))
        self.assertFalse(Vuelo.objects.get(codigo_vuelo="LA800").activo)
        self.assertEqual(self.client.get(reverse("catalogo:detalle", args=["LA800"])).status_code, 404)
        self.client.post(reverse("catalogo:reactivar", args=["LA800"]))
        self.assertTrue(Vuelo.objects.get(codigo_vuelo="LA800").activo)

    def test_validacion_formulario_vuelo(self):
        self.client.login(username="admin", password="Admin12345!")
        datos = {"aerolinea": 1, "codigo_vuelo": "la800", "origen": "A", "destino": "B",
                 "fecha_salida": "2026-12-01T10:00", "tarifa": 0, "cupos_disponibles": -1,
                 "estado": "PRG"}
        r = self.client.post(reverse("catalogo:crear"), datos)
        self.assertEqual(r.status_code, 200)
        errores = r.context["form"].errors
        self.assertIn("codigo_vuelo", errores)       # duplicado (case-insensitive)
        self.assertIn("tarifa", errores)
        self.assertIn("cupos_disponibles", errores)

    def test_registro_con_rut(self):
        datos = {"username": "nuevo", "first_name": "Ana", "last_name": "Pérez",
                 "email": "a@a.cl", "rut": "12.345.678-5", "telefono": "+56912345678",
                 "password1": "ClaveSegura#2026", "password2": "ClaveSegura#2026"}
        self.client.post(reverse("cuentas:registro"), datos)
        u = get_user_model().objects.get(username="nuevo")
        self.assertEqual(u.perfil.rut, "12345678-5")
        malo = dict(datos, username="otro", rut="12345678-9")
        r = self.client.post(reverse("cuentas:registro"), malo)
        self.assertFalse(get_user_model().objects.filter(username="otro").exists())

    def test_catalogo_busqueda_y_paginacion(self):
        r = self.client.get(reverse("catalogo:lista"), {"q": "lima"})
        self.assertEqual(len(r.context["page"]), 1)
        r = self.client.get(reverse("catalogo:lista"))
        self.assertEqual(len(r.context["page"]), 6)
        self.assertTrue(r.context["page"].has_next())
        r = self.client.get(reverse("catalogo:lista"), {"aerolinea": "1", "orden": "-tarifa"})
        self.assertEqual(r.status_code, 200)

    def test_digito_verificador(self):
        self.assertEqual(calcular_dv("12345678"), "5")
