import uuid

from django.conf import settings
from django.db import models


class Viaje(models.Model):
    """Un viaje solicitado por un pasajero, desde que lo pide hasta que finaliza."""

    class Estado(models.TextChoices):
        BUSCANDO = 'buscando', 'Buscando conductor'
        ACEPTADO = 'aceptado', 'Conductor asignado'
        EN_CAMINO_RECOJO = 'en_camino_recojo', 'Conductor en camino al recojo'
        EN_CURSO = 'en_curso', 'Viaje en curso'
        FINALIZADO = 'finalizado', 'Finalizado'
        CANCELADO = 'cancelado', 'Cancelado'

    class ModoTarifa(models.TextChoices):
        AUTOMATICA = 'automatica', 'Tarifa automática'
        OFERTA = 'oferta', 'El pasajero propone la tarifa'

    pasajero = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='viajes_como_pasajero'
    )
    conductor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='viajes_como_conductor'
    )

    origen_direccion = models.CharField(max_length=255)
    origen_lat = models.DecimalField(max_digits=10, decimal_places=7)
    origen_lng = models.DecimalField(max_digits=10, decimal_places=7)
    destino_direccion = models.CharField(max_length=255)
    destino_lat = models.DecimalField(max_digits=10, decimal_places=7)
    destino_lng = models.DecimalField(max_digits=10, decimal_places=7)

    distancia_km = models.DecimalField(max_digits=6, decimal_places=2)
    tiempo_estimado_min = models.PositiveIntegerField()

    modo_tarifa = models.CharField(max_length=15, choices=ModoTarifa.choices, default=ModoTarifa.AUTOMATICA)
    tarifa_sugerida = models.DecimalField(max_digits=8, decimal_places=2)
    tarifa_propuesta_pasajero = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tarifa_final = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class MetodoPago(models.TextChoices):
        EFECTIVO = 'efectivo', 'Efectivo'
        YAPE = 'yape', 'Yape'
        PLIN = 'plin', 'Plin'
        TARJETA = 'tarjeta', 'Tarjeta de crédito/débito'

    metodo_pago = models.CharField(max_length=10, choices=MetodoPago.choices, default=MetodoPago.EFECTIVO)
    propina = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BUSCANDO)

    placa_vehiculo = models.CharField(max_length=7, blank=True)
    modelo_vehiculo = models.CharField(max_length=100, blank=True)
    color_vehiculo = models.CharField(max_length=30, blank=True)

    emergencia_activada = models.BooleanField(default=False)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    hora_aceptado = models.DateTimeField(null=True, blank=True)
    hora_inicio = models.DateTimeField(null=True, blank=True)
    hora_fin = models.DateTimeField(null=True, blank=True)
    motivo_cancelacion = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'Viaje'
        verbose_name_plural = 'Viajes'

    def __str__(self):
        return f'Viaje #{self.pk} - {self.origen_direccion} -> {self.destino_direccion}'

    @property
    def activo(self):
        return self.estado in (
            self.Estado.BUSCANDO, self.Estado.ACEPTADO,
            self.Estado.EN_CAMINO_RECOJO, self.Estado.EN_CURSO,
        )

    @property
    def monto_comision_plataforma(self):
        if not self.tarifa_final:
            return 0
        return round(float(self.tarifa_final) * settings.COMISION_PLATAFORMA, 2)

    @property
    def monto_neto_conductor(self):
        if not self.tarifa_final:
            return 0
        return round(float(self.tarifa_final) - self.monto_comision_plataforma + float(self.propina), 2)


class OfertaViaje(models.Model):
    """Oferta de tarifa hecha por un conductor sobre un viaje en modo 'oferta' (estilo inDrive)."""

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        ACEPTADA = 'aceptada', 'Aceptada'
        RECHAZADA = 'rechazada', 'Rechazada'

    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, related_name='ofertas')
    conductor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ofertas_realizadas')
    monto_ofertado = models.DecimalField(max_digits=8, decimal_places=2)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.PENDIENTE)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['monto_ofertado']
        unique_together = ('viaje', 'conductor')

    def __str__(self):
        return f'Oferta S/ {self.monto_ofertado} de {self.conductor} para viaje #{self.viaje_id}'


class CompartirViaje(models.Model):
    """Enlace publico (sin login) para que un contacto de confianza siga el viaje en vivo."""

    viaje = models.OneToOneField(Viaje, on_delete=models.CASCADE, related_name='compartir')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Enlace de seguimiento viaje #{self.viaje_id}'
