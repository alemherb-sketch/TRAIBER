from django.conf import settings


def notificaciones_context(request):
    """Datos globales disponibles en todos los templates: moneda y viaje activo del usuario."""
    contexto = {
        'SIMBOLO_MONEDA': settings.SIMBOLO_MONEDA,
        'viaje_activo': None,
    }
    usuario = getattr(request, 'user', None)
    if usuario and usuario.is_authenticated:
        from viajes.models import Viaje
        if usuario.es_pasajero:
            contexto['viaje_activo'] = Viaje.objects.filter(
                pasajero=usuario
            ).exclude(estado__in=[Viaje.Estado.FINALIZADO, Viaje.Estado.CANCELADO]).first()
        elif usuario.es_conductor:
            contexto['viaje_activo'] = Viaje.objects.filter(
                conductor=usuario
            ).exclude(estado__in=[Viaje.Estado.FINALIZADO, Viaje.Estado.CANCELADO]).first()
    return contexto
