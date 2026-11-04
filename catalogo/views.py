from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .decorators import staff_required
from .forms import VueloForm
from .models import Aerolinea, Vuelo

ORDENES = {
    "fecha": "fecha_salida",
    "tarifa": "tarifa",
    "-tarifa": "-tarifa",
    "destino": "destino",
}


def lista(request):
    """R: catálogo público con búsqueda Q, filtros, orden y paginación."""
    vuelos = Vuelo.objects.select_related("aerolinea").filter(activo=True)

    q = request.GET.get("q", "").strip()
    if q:
        vuelos = vuelos.filter(
            Q(codigo_vuelo__icontains=q)
            | Q(origen__icontains=q)
            | Q(destino__icontains=q)
            | Q(descripcion__icontains=q)
        )

    aerolinea = request.GET.get("aerolinea", "")
    if aerolinea.isdigit():
        vuelos = vuelos.filter(aerolinea_id=int(aerolinea))

    estado = request.GET.get("estado", "")
    if estado in Vuelo.Estado.values:
        vuelos = vuelos.filter(estado=estado)

    orden = request.GET.get("orden", "fecha")
    vuelos = vuelos.order_by(ORDENES.get(orden, "fecha_salida"))

    page = Paginator(vuelos, 6).get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)

    return render(request, "catalogo/lista.html", {
        "page": page,
        "aerolineas": Aerolinea.objects.filter(activa=True),
        "estados": Vuelo.Estado.choices,
        "q": q,
        "aerolinea_sel": aerolinea,
        "estado_sel": estado,
        "orden_sel": orden,
        "querystring": params.urlencode(),
    })


def detalle(request, codigo_vuelo):
    vuelo = get_object_or_404(
        Vuelo.objects.select_related("aerolinea"),
        codigo_vuelo=codigo_vuelo,
        activo=True,
    )
    return render(request, "catalogo/detalle.html", {"vuelo": vuelo})


# ---------------- Backoffice (solo personal) ----------------

@staff_required
def gestion(request):
    vuelos = Vuelo.objects.select_related("aerolinea").order_by("-activo", "fecha_salida")
    return render(request, "catalogo/gestion.html", {"vuelos": vuelos})


@staff_required
def crear(request):
    if request.method == "POST":
        form = VueloForm(request.POST, request.FILES)
        if form.is_valid():
            vuelo = form.save()
            messages.success(request, f"Vuelo {vuelo.codigo_vuelo} creado correctamente.")
            return redirect("catalogo:gestion")
    else:
        form = VueloForm()
    return render(request, "catalogo/form.html", {"form": form, "titulo": "Nuevo vuelo"})


@staff_required
def editar(request, codigo_vuelo):
    vuelo = get_object_or_404(Vuelo, codigo_vuelo=codigo_vuelo)
    if request.method == "POST":
        form = VueloForm(request.POST, request.FILES, instance=vuelo)
        if form.is_valid():
            form.save()
            messages.success(request, f"Vuelo {vuelo.codigo_vuelo} actualizado.")
            return redirect("catalogo:gestion")
    else:
        form = VueloForm(instance=vuelo)
    return render(request, "catalogo/form.html", {
        "form": form, "titulo": f"Editar vuelo {vuelo.codigo_vuelo}",
    })


@staff_required
def eliminar(request, codigo_vuelo):
    """D: pantalla de confirmación previa + baja lógica (activo=False)."""
    vuelo = get_object_or_404(Vuelo, codigo_vuelo=codigo_vuelo, activo=True)
    if request.method == "POST":
        vuelo.activo = False
        vuelo.save(update_fields=["activo"])
        messages.warning(request, f"Vuelo {vuelo.codigo_vuelo} dado de baja.")
        return redirect("catalogo:gestion")
    return render(request, "catalogo/confirmar_eliminar.html", {"vuelo": vuelo})


@staff_required
@require_POST
def reactivar(request, codigo_vuelo):
    vuelo = get_object_or_404(Vuelo, codigo_vuelo=codigo_vuelo, activo=False)
    vuelo.activo = True
    vuelo.save(update_fields=["activo"])
    messages.success(request, f"Vuelo {vuelo.codigo_vuelo} reactivado.")
    return redirect("catalogo:gestion")
