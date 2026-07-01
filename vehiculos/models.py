from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


validador_placa = RegexValidator(
    regex=r'^[A-Z0-9]{6,7}$',
    message='Ingresa una placa peruana valida, ej: ABC-123 (sin guion).'
)


class Vehiculo(models.Model):
    """Vehiculo asociado a un conductor. Debe ser aprobado por el panel de administracion."""

    class TipoVehiculo(models.TextChoices):
        ECONOMICO = 'economico', 'Económico'
        CONFORT = 'confort', 'Confort'
        VAN = 'van', 'Van / Grupo grande'
        MOTO = 'moto', 'Moto taxi'

    conductor = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehiculo'
    )
    tipo_vehiculo = models.CharField(max_length=15, choices=TipoVehiculo.choices, default=TipoVehiculo.ECONOMICO)
    placa = models.CharField(max_length=7, unique=True, validators=[validador_placa])
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    anio = models.PositiveIntegerField(verbose_name='Año')
    soat_numero = models.CharField(max_length=30, verbose_name='N° de poliza SOAT')
    soat_vencimiento = models.DateField()
    soat_foto = models.ImageField(upload_to='documentos/soat/', blank=True, null=True)
    foto_vehiculo = models.ImageField(upload_to='vehiculos/', blank=True, null=True)
    aprobado = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'

    def __str__(self):
        return f'{self.marca} {self.modelo} - {self.placa}'

    @property
    def soat_vigente(self):
        from django.utils import timezone
        return self.soat_vencimiento >= timezone.now().date()
