from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Calificacion


@receiver(post_save, sender=Calificacion)
def actualizar_promedio_conductor(sender, instance, created, **kwargs):
    if not created:
        return
    receptor = instance.receptor
    if getattr(receptor, 'es_conductor', False) and hasattr(receptor, 'perfil_conductor'):
        promedio = Calificacion.objects.filter(receptor=receptor).aggregate(promedio=Avg('puntuacion'))['promedio']
        receptor.perfil_conductor.calificacion_promedio = round(promedio or 5, 2)
        receptor.perfil_conductor.save(update_fields=['calificacion_promedio'])
