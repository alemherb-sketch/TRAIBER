import uuid

from django.db import models

from viajes.models import Viaje


class Pago(models.Model):
    """Registro de pago de un viaje. Yape/Plin/Tarjeta se simulan (no hay pasarela real conectada)."""

    class MetodoPago(models.TextChoices):
        EFECTIVO = 'efectivo', 'Efectivo'
        YAPE = 'yape', 'Yape'
        PLIN = 'plin', 'Plin'
        TARJETA = 'tarjeta', 'Tarjeta de crédito/débito'

    class EstadoPago(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        PAGADO = 'pagado', 'Pagado'
        FALLIDO = 'fallido', 'Fallido'

    viaje = models.OneToOneField(Viaje, on_delete=models.CASCADE, related_name='pago')
    metodo = models.CharField(max_length=10, choices=MetodoPago.choices)
    monto = models.DecimalField(max_digits=8, decimal_places=2, help_text='Monto en soles (S/)')
    estado = models.CharField(max_length=10, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE)
    referencia = models.CharField(max_length=40, unique=True, default=uuid.uuid4, editable=False)
    creado = models.DateTimeField(auto_now_add=True)
    procesado = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f'Pago S/ {self.monto} ({self.get_metodo_display()}) - viaje #{self.viaje_id}'

    def marcar_pagado(self):
        from django.utils import timezone
        self.estado = self.EstadoPago.PAGADO
        self.procesado = timezone.now()
        self.save(update_fields=['estado', 'procesado'])
