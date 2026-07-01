from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from .models import CompartirViaje, Viaje


class ViajeConsumer(JsonWebsocketConsumer):
    """Canal por viaje: ubicacion del conductor en vivo, cambios de estado y emergencia."""

    def connect(self):
        self.viaje_id = self.scope['url_route']['kwargs']['viaje_id']
        self.grupo = f'viaje_{self.viaje_id}'
        usuario = self.scope.get('user')

        if not usuario or not usuario.is_authenticated:
            self.close()
            return

        try:
            viaje = Viaje.objects.get(pk=self.viaje_id)
        except Viaje.DoesNotExist:
            self.close()
            return

        if viaje.pasajero_id != usuario.id and viaje.conductor_id != usuario.id:
            self.close()
            return

        async_to_sync(self.channel_layer.group_add)(self.grupo, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        if hasattr(self, 'grupo'):
            async_to_sync(self.channel_layer.group_discard)(self.grupo, self.channel_name)

    def receive_json(self, content, **kwargs):
        tipo = content.get('tipo')
        usuario = self.scope['user']

        if tipo == 'ubicacion' and usuario.id:
            async_to_sync(self.channel_layer.group_send)(self.grupo, {
                'type': 'viaje.ubicacion',
                'lat': content.get('lat'),
                'lng': content.get('lng'),
            })
        elif tipo == 'emergencia':
            Viaje.objects.filter(pk=self.viaje_id).update(emergencia_activada=True)
            async_to_sync(self.channel_layer.group_send)(self.grupo, {
                'type': 'viaje.emergencia',
                'usuario': usuario.get_full_name() or usuario.username,
            })

    # Handlers invocados via group_send (deben coincidir con 'type' con puntos -> guion bajo)
    def viaje_ubicacion(self, event):
        self.send_json({'tipo': 'ubicacion', 'lat': event['lat'], 'lng': event['lng']})

    def viaje_estado(self, event):
        self.send_json({'tipo': 'estado', 'estado': event['estado'], 'mensaje': event.get('mensaje', '')})

    def viaje_emergencia(self, event):
        self.send_json({'tipo': 'emergencia', 'usuario': event['usuario']})

    def viaje_oferta(self, event):
        self.send_json({'tipo': 'oferta', 'oferta_id': event['oferta_id'], 'monto': event['monto'],
                         'conductor': event['conductor']})


class NotificacionesConductorConsumer(JsonWebsocketConsumer):
    """Canal para conductores disponibles: nuevas solicitudes de viaje en la zona."""

    def connect(self):
        usuario = self.scope.get('user')
        if not usuario or not usuario.is_authenticated or not usuario.es_conductor:
            self.close()
            return

        self.grupo_general = 'conductores_disponibles'
        self.grupo_personal = f'conductor_{usuario.id}'
        async_to_sync(self.channel_layer.group_add)(self.grupo_general, self.channel_name)
        async_to_sync(self.channel_layer.group_add)(self.grupo_personal, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        if hasattr(self, 'grupo_general'):
            async_to_sync(self.channel_layer.group_discard)(self.grupo_general, self.channel_name)
            async_to_sync(self.channel_layer.group_discard)(self.grupo_personal, self.channel_name)

    def nueva_solicitud(self, event):
        self.send_json({'tipo': 'nueva_solicitud', 'viaje_id': event['viaje_id']})

    def solicitud_tomada(self, event):
        self.send_json({'tipo': 'solicitud_tomada', 'viaje_id': event['viaje_id']})

    def oferta_respondida(self, event):
        self.send_json({'tipo': 'oferta_respondida', 'viaje_id': event['viaje_id'], 'estado': event['estado']})


class SeguimientoPublicoConsumer(JsonWebsocketConsumer):
    """Canal publico (sin login) para que un contacto de confianza vea el viaje en vivo via token."""

    def connect(self):
        token = self.scope['url_route']['kwargs']['token']
        try:
            enlace = CompartirViaje.objects.select_related('viaje').get(token=token, activo=True)
        except CompartirViaje.DoesNotExist:
            self.close()
            return

        self.grupo = f'viaje_{enlace.viaje_id}'
        async_to_sync(self.channel_layer.group_add)(self.grupo, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        if hasattr(self, 'grupo'):
            async_to_sync(self.channel_layer.group_discard)(self.grupo, self.channel_name)

    def viaje_ubicacion(self, event):
        self.send_json({'tipo': 'ubicacion', 'lat': event['lat'], 'lng': event['lng']})

    def viaje_estado(self, event):
        self.send_json({'tipo': 'estado', 'estado': event['estado'], 'mensaje': event.get('mensaje', '')})

    def viaje_emergencia(self, event):
        self.send_json({'tipo': 'emergencia', 'usuario': event['usuario']})
