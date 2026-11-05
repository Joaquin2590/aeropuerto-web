# AeroConecta Chile — Aeropuerto y reserva de vuelos

Bictácora de la unidad 3 y la unidad 4

## Fecha idea: 22-10-2026

## Ficha de registro

| Campo | Detalle |
| --- | --- |
| Nombre de la Organización | AeroConecta Chile |
| Modelo de Negocio | Aeropuerto, gestión y reserva de vuelos |
| Integrantes del Equipo | Joaquín Rodríguez — *21675169-8*|
| Entidad de Contexto (ORM) | `Aerolinea` |
| Entidad Principal Gestionable (ORM) | `Vuelo` |
| Propósito de la Sesión (`request.session`) | Carpeta de reserva de vuelos con cálculo de tasa de embarque e IVA y control de cupos |

## fecha de inicio: 27-10-26 

## Funcionalidades

- **Catálogo público**: tarjetas Bootstrap, búsqueda multicampo con `Q` (código, origen, destino, descripción), filtros por aerolínea y estado, ordenamiento y paginación (6 por página). Detalle por slug (`/vuelo/LA800/`).
- **Carpeta de reserva (sesión)**: agregar vuelos validando cupos, cambiar pasajeros, quitar vuelos, vaciar, desglose (subtotal + tasa de embarque + IVA 19 % = total) y contador global en el navbar mediante un *context processor*. Al confirmar se genera un comprobante simulado y se vacía la sesión.
- **Backoffice** (`/gestion/`, solo `is_staff`): crear, editar y dar de baja (con pantalla de confirmación) / reactivar vuelos. Además, Django Admin personalizado.
- **Usuarios**: registro (con RUT validado y teléfono), login, logout (POST) y perfil con rol institucional.

## Básico git

```bash
# 1. Clonar
git clone https://github.com/Joaquin2590/aeropuerto-web.git
cd aeropuerto-web
git add .
git commit -m "proyector terminado"
git push origin main

# 2. Entorno virtual
python -m venv .venv
.venv\Scripts\activate          

# 3. Dependencias
pip install -r requirements.txt

# 4. Variables de entorno
copy .env.example .env       
# Edita .env y define SECRET_KEY

# 5. Base de datos y datos de prueba
python manage.py migrate
python manage.py poblar_datos

# 6. Ejecutar
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/> · Admin: <http://127.0.0.1:8000/admin/>

## Credenciales de prueba (creadas por `poblar_datos`)

| Usuario | Contraseña | Rol |
| --- | --- | --- |
| `admin` | `Admin12345!` | Administrador / personal (`is_staff`) |
| `usuario` | `Usuario12345!` | Pasajero estándar |

## Tests

```bash
python manage.py test
```

# fecha 04-11-2026

## Bitácora de prompts (uso de IA)

> **Importante:** edita esta sección con tus prompts y tus adaptaciones reales. El docente puede preguntar por ellos en la defensa.

### Caso 1 — Arquitectura y modelado ORM
- **Prompt:** "Tengo un proyecto Django de aeropuerto con `Aerolinea` (contexto) y `Vuelo` (principal). Necesito ForeignKey con PROTECT, slug único, `MinValueValidator`, `choices` de estado, ImageField y baja lógica."
- **Respuesta técnica:** `Vuelo.aerolinea` con `on_delete=PROTECT`, `codigo_vuelo` como `SlugField(unique=True)`, `TextChoices` para el estado y campo booleano `activo`.
- **Adaptación aplicada:** el estado quedó con códigos de 3 letras (PRG/EMB/RET/CAN); agregué `ordering` por fecha de salida y la propiedad `reservable`.

### Caso 2 — Optimización de consultas
- **Prompt:** "¿Cómo evito consultas N+1 al listar vuelos con el nombre de su aerolínea en el catálogo y en la carpeta de sesión?"
- **Respuesta técnica:** usar `select_related("aerolinea")` y filtrar con `codigo_vuelo__in` en una sola consulta.
- **Adaptación aplicada:** lo apliqué en `catalogo/views.py`, `reservas/services.py` y `VueloAdmin` (`list_select_related`).

### Caso 3 — Seguridad y sesiones
- **Prompt:** "¿Cómo protejo las rutas de gestión para que solo entre el personal y cómo guardo una carpeta de reserva en `request.session` sin confiar en lo que envía el cliente?"
- **Respuesta técnica:** `@login_required` + `@user_passes_test(is_staff)`, formularios POST con `{% csrf_token %}`, y revalidar cupos/estado contra la BD en cada operación.
- **Adaptación aplicada:** decorador `staff_required` que redirige a una página 403 propia; la sesión guarda solo `{código: pasajeros}` y los precios se recalculan siempre desde la BD.
