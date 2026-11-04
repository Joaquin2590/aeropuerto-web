from django.contrib.auth.decorators import login_required, user_passes_test


def es_personal(user):
    return user.is_active and user.is_staff


def staff_required(view):
    """Exige sesión iniciada (login_required) y rol de personal (is_staff)."""
    return login_required(
        user_passes_test(es_personal, login_url="cuentas:acceso_denegado")(view)
    )
