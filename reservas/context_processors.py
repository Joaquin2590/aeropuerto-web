from .services import obtener_carpeta


def carpeta_reserva(request):
    """Inyecta en todas las plantillas el número de vuelos en la carpeta (badge del navbar)."""
    return {"carpeta_count": len(obtener_carpeta(request.session))}
