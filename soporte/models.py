from django.conf import settings
from django.db import models

from viajes.models import Viaje


class TicketSoporte(models.Model):
    """Ticket de soporte tecnico: dudas, objetos perdidos, reembolsos, quejas."""

    class Categoria(models.TextChoices):
        DUDA = 'duda', 'Duda general'
        OBJETO_PERDIDO = 'objeto_perdido', 'Objeto perdido'
        REEMBOLSO = 'reembolso', 'Reembolso'
        QUEJA = 'queja', 'Queja sobre un viaje'
        OTRO = 'otro', 'Otro'

    class Estado(models.TextChoices):
        ABIERTO = 'abierto', 'Abierto'
        EN_PROCESO = 'en_proceso', 'En proceso'
        RESUELTO = 'resuelto', 'Resuelto'
        CERRADO = 'cerrado', 'Cerrado'

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets_soporte')
    viaje = models.ForeignKey(Viaje, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    categoria = models.CharField(max_length=20, choices=Categoria.choices, default=Categoria.DUDA)
    asunto = models.CharField(max_length=150)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.ABIERTO)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-actualizado']
        verbose_name = 'Ticket de soporte'
        verbose_name_plural = 'Tickets de soporte'

    def __str__(self):
        return f'Ticket #{self.pk} - {self.asunto} ({self.get_estado_display()})'


class MensajeSoporte(models.Model):
    """Mensaje dentro del chat de un ticket de soporte."""

    ticket = models.ForeignKey(TicketSoporte, on_delete=models.CASCADE, related_name='mensajes')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    es_staff = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['creado']

    def __str__(self):
        return f'Mensaje de {self.autor} en ticket #{self.ticket_id}'
