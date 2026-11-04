from django.urls import path

from . import views

app_name = "catalogo"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("vuelo/<slug:codigo_vuelo>/", views.detalle, name="detalle"),
    path("gestion/", views.gestion, name="gestion"),
    path("gestion/nuevo/", views.crear, name="crear"),
    path("gestion/<slug:codigo_vuelo>/editar/", views.editar, name="editar"),
    path("gestion/<slug:codigo_vuelo>/eliminar/", views.eliminar, name="eliminar"),
    path("gestion/<slug:codigo_vuelo>/reactivar/", views.reactivar, name="reactivar"),
]
