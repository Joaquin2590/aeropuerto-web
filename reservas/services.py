"""Lógica de la carpeta de reserva guardada en request.session (sin tocar la BD)."""
from django.conf import settings

from catalogo.models import Vuelo

SESSION_KEY = "carpeta_reserva"  # {"LA800": 2, "H2305": 1}  -> código: pasajeros


def obtener_carpeta(session) -> dict:
    return session.get(SESSION_KEY, {})


def guardar_carpeta(session, carpeta: dict):
    session[SESSION_KEY] = carpeta
    session.modified = True


def vaciar_carpeta(session):
    session.pop(SESSION_KEY, None)
    session.modified = True


def calcular_resumen(session) -> dict:
    """Devuelve ítems + subtotal, tasa de embarque, IVA y total (enteros en CLP)."""
    carpeta = obtener_carpeta(session)
    vuelos = Vuelo.objects.select_related("aerolinea").filter(
        codigo_vuelo__in=carpeta.keys(), activo=True
    )
    items, subtotal, pasajeros_total = [], 0, 0
    for vuelo in vuelos:
        pax = carpeta[vuelo.codigo_vuelo]
        linea = vuelo.tarifa * pax
        subtotal += linea
        pasajeros_total += pax
        items.append({
            "vuelo": vuelo,
            "pasajeros": pax,
            "subtotal": linea,
            "excede_cupos": pax > vuelo.cupos_disponibles or vuelo.estado == Vuelo.Estado.CANCELADO,
        })

    tasa = pasajeros_total * settings.TASA_EMBARQUE_POR_PASAJERO
    base = subtotal + tasa
    iva = (base * settings.IVA_PORCENTAJE + 50) // 100
    return {
        "items": items,
        "subtotal": subtotal,
        "tasa_embarque": tasa,
        "iva": iva,
        "total": base + iva,
        "pasajeros_total": pasajeros_total,
        "hay_problemas": any(i["excede_cupos"] for i in items),
    }
