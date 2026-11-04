from django.conf import settings
from django.db import models

from .validators import validar_rut


class PerfilUsuario(models.Model):
    class Rol(models.TextChoices):
        PASAJERO = "PAS", "Pasajero"
        OPERADOR = "OPE", "Operador de aeropuerto"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil"
    )
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut])
    telefono = models.CharField("Teléfono", max_length=20, blank=True)
    rol = models.CharField(max_length=3, choices=Rol.choices, default=Rol.PASAJERO)

    def __str__(self):
        return f"Perfil de {self.user.username}"
