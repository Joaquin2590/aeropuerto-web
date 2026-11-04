from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import PerfilUsuario

User = get_user_model()


class PerfilInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    extra = 0


admin.site.unregister(User)


@admin.register(User)
class UsuarioAdmin(UserAdmin):
    inlines = [PerfilInline]
    list_display = ("username", "email", "is_staff", "is_active")


@admin.register(PerfilUsuario)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "rut", "telefono", "rol")
    list_filter = ("rol",)
    search_fields = ("user__username", "rut")
