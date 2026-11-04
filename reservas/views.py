import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from catalogo.models import Vuelo

from . import services


def _pasajeros(request):
    """Lee y valida el campo 'pasajeros' del POST; None si es inválido."""
    try:
        n = int(request.POST.get("pasajeros", "1"))
    except ValueError:
        return None
    return n if n >= 1 else None


def ver_carpeta(request):
    return render(request, "reservas/carpeta.html", services.calcular_resumen(request.session))


@require_POST
def agregar(request, codigo_vuelo):
    vuelo = get_object_or_404(Vuelo, codigo_vuelo=codigo_vuelo, activo=True)
    pax = _pasajeros(request)
    if pax is None:
        messages.error(request, "Indica una cantidad de pasajeros válida (mínimo 1).")
        return redirect(vuelo)
    if vuelo.estado == Vuelo.Estado.CANCELADO:
        messages.error(request, "Este vuelo está cancelado y no se puede reservar.")
        return redirect(vuelo)

    carpeta = dict(services.obtener_carpeta(request.session))
    total = carpeta.get(vuelo.codigo_vuelo, 0) + pax
    if total > vuelo.cupos_disponibles:
        messages.error(
            request,
            f"No hay cupos suficientes en {vuelo.codigo_vuelo}: quedan {vuelo.cupos_disponibles}.",
        )
        return redirect(vuelo)

    carpeta[vuelo.codigo_vuelo] = total
    services.guardar_carpeta(request.session, carpeta)
    messages.success(request, f"{vuelo.codigo_vuelo} agregado a tu carpeta ({total} pasajero/s).")
    return redirect("reservas:carpeta")


@require_POST
def modificar(request, codigo_vuelo):
    carpeta = dict(services.obtener_carpeta(request.session))
    if codigo_vuelo not in carpeta:
        return redirect("reservas:carpeta")
    vuelo = get_object_or_404(Vuelo, codigo_vuelo=codigo_vuelo, activo=True)
    pax = _pasajeros(request)
    if pax is None:
        messages.error(request, "Cantidad de pasajeros inválida.")
    elif pax > vuelo.cupos_disponibles:
        messages.error(request, f"Solo quedan {vuelo.cupos_disponibles} cupos en {codigo_vuelo}.")
    else:
        carpeta[codigo_vuelo] = pax
        services.guardar_carpeta(request.session, carpeta)
        messages.success(request, f"Pasajeros de {codigo_vuelo} actualizados a {pax}.")
    return redirect("reservas:carpeta")


@require_POST
def quitar(request, codigo_vuelo):
    carpeta = dict(services.obtener_carpeta(request.session))
    if carpeta.pop(codigo_vuelo, None) is not None:
        services.guardar_carpeta(request.session, carpeta)
        messages.info(request, f"{codigo_vuelo} eliminado de la carpeta.")
    return redirect("reservas:carpeta")


@require_POST
def vaciar(request):
    services.vaciar_carpeta(request.session)
    messages.info(request, "Tu carpeta de reserva quedó vacía.")
    return redirect("reservas:carpeta")


@login_required
@require_POST
def confirmar(request):
    """Genera el comprobante simulado y vacía la sesión."""
    resumen = services.calcular_resumen(request.session)
    if not resumen["items"]:
        messages.error(request, "Tu carpeta está vacía.")
        return redirect("reservas:carpeta")
    if resumen["hay_problemas"]:
        messages.error(request, "Hay vuelos sin cupos suficientes o cancelados. Revisa tu carpeta.")
        return redirect("reservas:carpeta")

    request.session["comprobante"] = {
        "numero": "CMP-" + uuid.uuid4().hex[:8].upper(),
        "fecha": timezone.localtime().strftime("%d-%m-%Y %H:%M"),
        "pasajero": request.user.get_full_name() or request.user.username,
        "items": [
            {
                "codigo": i["vuelo"].codigo_vuelo,
                "ruta": f"{i['vuelo'].origen} → {i['vuelo'].destino}",
                "pasajeros": i["pasajeros"],
                "tarifa": i["vuelo"].tarifa,
                "subtotal": i["subtotal"],
            }
            for i in resumen["items"]
        ],
        "subtotal": resumen["subtotal"],
        "tasa_embarque": resumen["tasa_embarque"],
        "iva": resumen["iva"],
        "total": resumen["total"],
    }
    services.vaciar_carpeta(request.session)
    return redirect("reservas:comprobante")


@login_required
def comprobante(request):
    datos = request.session.get("comprobante")
    if not datos:
        messages.info(request, "Aún no tienes un comprobante generado.")
        return redirect("catalogo:lista")
    return render(request, "reservas/comprobante.html", {"c": datos})
