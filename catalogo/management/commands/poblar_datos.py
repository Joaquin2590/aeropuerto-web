from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from catalogo.models import Aerolinea, Vuelo
from cuentas.models import PerfilUsuario

AEROLINEAS = [
    ("LATAM Airlines", "LA", "Chile", "https://www.latamairlines.com"),
    ("SKY Airline", "H2", "Chile", "https://www.skyairline.com"),
    ("JetSMART", "JA", "Chile", "https://jetsmart.com"),
    ("Aerolíneas Argentinas", "AR", "Argentina", "https://www.aerolineas.com.ar"),
]

# código, aerolínea (IATA), origen, destino, días desde hoy, tarifa, cupos, estado, descripción
VUELOS = [
    ("LA800", "LA", "Santiago", "Buenos Aires", 3, 125000, 40, "PRG", "Vuelo directo a Buenos Aires, 1 equipaje de mano incluido."),
    ("LA532", "LA", "Santiago", "Lima", 4, 98000, 25, "PRG", "Conexión rápida a la capital peruana."),
    ("H2305", "H2", "Santiago", "Punta Arenas", 5, 89000, 30, "PRG", "Puerta de entrada a la Patagonia austral."),
    ("H2121", "H2", "Santiago", "Calama", 2, 54000, 12, "EMB", "Ideal para visitar San Pedro de Atacama."),
    ("JA402", "JA", "Santiago", "Puerto Montt", 6, 47000, 50, "PRG", "Lagos y volcanes del sur de Chile."),
    ("JA250", "JA", "Santiago", "Isla de Pascua", 10, 310000, 8, "RET", "Vuelo con demora por condiciones climáticas."),
    ("AR1161", "AR", "Santiago", "Mendoza", 7, 72000, 20, "PRG", "Cruce de la cordillera, ruta del vino."),
    ("LA601", "LA", "Santiago", "Cusco", 8, 165000, 5, "PRG", "Acceso a Machu Picchu."),
    ("H2777", "H2", "Santiago", "Arica", 9, 78000, 0, "CAN", "Vuelo cancelado por mantenimiento."),
]


class Command(BaseCommand):
    help = "Carga aerolíneas, vuelos y usuarios de prueba (se puede ejecutar varias veces)."

    def handle(self, *args, **options):
        aerolineas = {}
        for nombre, iata, pais, web in AEROLINEAS:
            obj, _ = Aerolinea.objects.update_or_create(
                codigo_iata=iata,
                defaults={"nombre": nombre, "pais_origen": pais, "sitio_web": web, "activa": True},
            )
            aerolineas[iata] = obj

        imagenes = sorted(Path(settings.BASE_DIR, "imagen").glob("viajes-*.png"))
        ahora = timezone.now().replace(minute=0, second=0, microsecond=0)

        for i, (codigo, iata, origen, destino, dias, tarifa, cupos, estado, desc) in enumerate(VUELOS):
            vuelo, creado = Vuelo.objects.update_or_create(
                codigo_vuelo=codigo,
                defaults={
                    "aerolinea": aerolineas[iata], "origen": origen, "destino": destino,
                    "fecha_salida": ahora + timedelta(days=dias, hours=i),
                    "descripcion": desc, "tarifa": tarifa, "cupos_disponibles": cupos,
                    "estado": estado, "activo": True,
                },
            )
            if imagenes and not vuelo.imagen:
                origen_img = imagenes[i % len(imagenes)]
                vuelo.imagen.save(f"{codigo}.jpg", ContentFile(origen_img.read_bytes()), save=True)

        User = get_user_model()
        admin, nuevo = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@aeroconecta.cl", "is_staff": True, "is_superuser": True},
        )
        if nuevo:
            admin.set_password("Admin12345!")
            admin.save()
        PerfilUsuario.objects.get_or_create(
            user=admin,
            defaults={"rut": "11111111-1", "telefono": "+56911111111", "rol": PerfilUsuario.Rol.OPERADOR},
        )

        usuario, nuevo = User.objects.get_or_create(
            username="usuario", defaults={"email": "usuario@aeroconecta.cl"},
        )
        if nuevo:
            usuario.set_password("Usuario12345!")
            usuario.save()
        PerfilUsuario.objects.get_or_create(
            user=usuario,
            defaults={"rut": "22222222-2", "telefono": "+56922222222", "rol": PerfilUsuario.Rol.PASAJERO},
        )

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {Aerolinea.objects.count()} aerolíneas, {Vuelo.objects.count()} vuelos, "
            "usuarios 'admin' y 'usuario'."
        ))
