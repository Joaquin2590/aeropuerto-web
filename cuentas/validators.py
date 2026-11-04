import re

from django.core.exceptions import ValidationError


def calcular_dv(numero: str) -> str:
    suma, factor = 0, 2
    for digito in reversed(numero):
        suma += int(digito) * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - (suma % 11)
    return "0" if resto == 11 else "K" if resto == 10 else str(resto)


def normalizar_rut(valor: str) -> str:
    """'12.345.678-5' -> '12345678-5'."""
    limpio = re.sub(r"[.\s]", "", valor or "").upper()
    return limpio


def validar_rut(valor):
    rut = normalizar_rut(valor)
    if not re.fullmatch(r"\d{7,8}-[\dK]", rut):
        raise ValidationError("Formato de RUT inválido. Ejemplo: 12345678-5")
    cuerpo, dv = rut.split("-")
    if calcular_dv(cuerpo) != dv:
        raise ValidationError("El RUT ingresado no es válido (dígito verificador incorrecto).")
