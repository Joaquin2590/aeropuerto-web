from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Aerolinea(models.Model):
    """Entidad de contexto / agrupación."""

    nombre = models.CharField(max_length=100, unique=True)
    codigo_iata = models.CharField("Código IATA", max_length=3, unique=True)
    pais_origen = models.CharField("País de origen", max_length=60)
    sitio_web = models.URLField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Vuelo(models.Model):
    """Entidad principal gestionable."""

    class Estado(models.TextChoices):
        PROGRAMADO = "PRG", "Programado"
        EMBARCANDO = "EMB", "Embarcando"
        RETRASADO = "RET", "Retrasado"
        CANCELADO = "CAN", "Cancelado"

    aerolinea = models.ForeignKey(
        Aerolinea, on_delete=models.PROTECT, related_name="vuelos"
    )
    codigo_vuelo = models.SlugField(max_length=10, unique=True)  # ej. LA800
    origen = models.CharField(max_length=80)
    destino = models.CharField(max_length=80)
    fecha_salida = models.DateTimeField()
    descripcion = models.TextField(blank=True)
    tarifa = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    cupos_disponibles = models.IntegerField(validators=[MinValueValidator(0)])
    estado = models.CharField(
        max_length=3, choices=Estado.choices, default=Estado.PROGRAMADO
    )
    imagen = models.ImageField(upload_to="vuelos/", blank=True, null=True)
    activo = models.BooleanField(default=True)  # baja lógica

    class Meta:
        ordering = ["fecha_salida"]

    def __str__(self):
        return f"{self.codigo_vuelo}: {self.origen} → {self.destino}"

    def get_absolute_url(self):
        return reverse("catalogo:detalle", args=[self.codigo_vuelo])

    @property
    def reservable(self):
        """Se puede agregar a la carpeta de reserva."""
        return (
            self.activo
            and self.estado != self.Estado.CANCELADO
            and self.cupos_disponibles > 0
        )
