from django.urls import path

from . import views

app_name = "reservas"

urlpatterns = [
    path("", views.ver_carpeta, name="carpeta"),
    path("agregar/<slug:codigo_vuelo>/", views.agregar, name="agregar"),
    path("modificar/<slug:codigo_vuelo>/", views.modificar, name="modificar"),
    path("quitar/<slug:codigo_vuelo>/", views.quitar, name="quitar"),
    path("vaciar/", views.vaciar, name="vaciar"),
    path("confirmar/", views.confirmar, name="confirmar"),
    path("comprobante/", views.comprobante, name="comprobante"),
]
