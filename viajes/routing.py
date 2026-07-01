from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/viaje/(?P<viaje_id>\d+)/$', consumers.ViajeConsumer.as_asgi()),
    re_path(r'^ws/conductor/notificaciones/$', consumers.NotificacionesConductorConsumer.as_asgi()),
    re_path(r'^ws/seguimiento/(?P<token>[0-9a-f-]+)/$', consumers.SeguimientoPublicoConsumer.as_asgi()),
]
