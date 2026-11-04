from django.conf import settings
from django.contrib import admin

from .models import Aerolinea, Vuelo

admin.site.site_header = f"{settings.NOMBRE_ORGANIZACION} - Panel de Control"
admin.site.site_title = f"{settings.NOMBRE_ORGANIZACION} Admin"
admin.site.index_title = "Gestión Operativa de Recursos y Servicios"


@admin.register(Aerolinea)
class AerolineaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo_iata", "pais_origen", "activa")
    list_filter = ("activa", "pais_origen")
    search_fields = ("nombre", "codigo_iata")


@admin.register(Vuelo)
class VueloAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_vuelo", "origen", "destino", "aerolinea",
        "tarifa", "cupos_disponibles", "estado", "activo",
    )
    list_filter = ("aerolinea", "estado", "activo")
    search_fields = ("codigo_vuelo", "origen", "destino", "descripcion")
    list_editable = ("cupos_disponibles", "estado", "activo")
    list_select_related = ("aerolinea",)
    fieldsets = (
        ("Identificación", {"fields": ("codigo_vuelo", "aerolinea")}),
        ("Ruta y horario", {"fields": ("origen", "destino", "fecha_salida", "descripcion")}),
        ("Tarifa y capacidad", {"fields": ("tarifa", "cupos_disponibles", "estado")}),
        ("Multimedia y vigencia", {"fields": ("imagen", "activo")}),
    )
