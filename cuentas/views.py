from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import RegistroForm


class IngresoView(LoginView):
    template_name = "cuentas/login.html"
    redirect_authenticated_user = True

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for campo in form.fields.values():
            campo.widget.attrs["class"] = "form-control"
        return form


def registro(request):
    if request.user.is_authenticated:
        return redirect("catalogo:lista")
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido/a, {user.first_name or user.username}!")
            return redirect("catalogo:lista")
    else:
        form = RegistroForm()
    return render(request, "cuentas/registro.html", {"form": form})


def acceso_denegado(request):
    return render(request, "cuentas/acceso_denegado.html", status=403)
