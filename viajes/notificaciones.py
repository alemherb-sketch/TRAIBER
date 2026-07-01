"""Helpers para enviar eventos en vivo por WebSocket desde vistas normales (sync)."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def _enviar(grupo, evento):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(grupo, evento)


def notificar_estado_viaje(viaje_id, estado, mensaje=''):
    _enviar(f'viaje_{viaje_id}', {'type': 'viaje.estado', 'estado': estado, 'mensaje': mensaje})


def notificar_oferta_viaje(viaje_id, oferta):
    _enviar(f'viaje_{viaje_id}', {
        'type': 'viaje.oferta',
        'oferta_id': oferta.id,
        'monto': str(oferta.monto_ofertado),
        'conductor': oferta.conductor.get_full_name() or oferta.conductor.username,
    })


def notificar_nueva_solicitud_a_conductores(viaje_id):
    _enviar('conductores_disponibles', {'type': 'nueva.solicitud', 'viaje_id': viaje_id})


def notificar_solicitud_tomada(viaje_id):
    _enviar('conductores_disponibles', {'type': 'solicitud.tomada', 'viaje_id': viaje_id})


def notificar_oferta_respondida(conductor_id, viaje_id, estado):
    _enviar(f'conductor_{conductor_id}', {'type': 'oferta.respondida', 'viaje_id': viaje_id, 'estado': estado})
