from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import PerfilUsuario
from .validators import normalizar_rut, validar_rut

User = get_user_model()


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    rut = forms.CharField(max_length=12, help_text="Ej: 12345678-5")
    telefono = forms.CharField(max_length=20, required=False, label="Teléfono")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs.setdefault("class", "form-control")

    def clean_rut(self):
        rut = normalizar_rut(self.cleaned_data["rut"])
        validar_rut(rut)
        if PerfilUsuario.objects.filter(rut=rut).exists():
            raise forms.ValidationError("Ya existe un usuario con ese RUT.")
        return rut

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Todo registro público es Pasajero; el rol de operador lo asigna el admin.
            PerfilUsuario.objects.create(
                user=user,
                rut=self.cleaned_data["rut"],
                telefono=self.cleaned_data["telefono"],
                rol=PerfilUsuario.Rol.PASAJERO,
            )
        return user
