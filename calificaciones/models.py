from django.conf import settings
from django.db import models

from viajes.models import Viaje


class Calificacion(models.Model):
    """Calificacion bidireccional: el pasajero califica al conductor y viceversa, por viaje."""

    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, related_name='calificaciones')
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calificaciones_hechas'
    )
    receptor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calificaciones_recibidas'
    )
    puntuacion = models.PositiveSmallIntegerField()
    comentario = models.CharField(max_length=300, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('viaje', 'autor')
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'

    def __str__(self):
        return f'{self.autor} califico con {self.puntuacion}★ a {self.receptor} (viaje #{self.viaje_id})'
