from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "cuentas"

urlpatterns = [
    path("login/", views.IngresoView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),  # solo POST
    path("registro/", views.registro, name="registro"),
    path("acceso-denegado/", views.acceso_denegado, name="acceso_denegado"),
]
