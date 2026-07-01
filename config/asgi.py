"""
Configuracion ASGI para el proyecto TRAIBER.
Sirve HTTP normal y WebSockets (tracking en vivo, notificaciones de viajes).
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import viajes.routing

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(viajes.routing.websocket_urlpatterns)
    ),
})
