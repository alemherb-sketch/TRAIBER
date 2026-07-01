from django.urls import path

from . import views

app_name = 'viajes'

urlpatterns = [
    # Pasajero
    path('pasajero/', views.panel_pasajero, name='panel_pasajero'),
    path('pasajero/solicitar/', views.solicitar_viaje, name='solicitar_viaje'),
    path('pasajero/historial/', views.historial_pasajero, name='historial_pasajero'),
    path('oferta/<int:oferta_id>/aceptar/', views.aceptar_oferta, name='aceptar_oferta'),

    # Conductor
    path('conductor/', views.panel_conductor, name='panel_conductor'),
    path('conductor/disponibilidad/', views.actualizar_disponibilidad, name='actualizar_disponibilidad'),
    path('conductor/ubicacion/', views.actualizar_ubicacion_conductor, name='actualizar_ubicacion_conductor'),
    path('conductor/solicitudes.json', views.solicitudes_json, name='solicitudes_json'),
    path('conductor/historial/', views.historial_conductor, name='historial_conductor'),
    path('<int:viaje_id>/aceptar/', views.aceptar_viaje, name='aceptar_viaje'),
    path('<int:viaje_id>/ofertar/', views.ofertar_viaje, name='ofertar_viaje'),
    path('<int:viaje_id>/iniciar/', views.iniciar_viaje, name='iniciar_viaje'),
    path('<int:viaje_id>/finalizar/', views.finalizar_viaje, name='finalizar_viaje'),

    # Comun
    path('<int:viaje_id>/', views.ver_viaje, name='ver_viaje'),
    path('<int:viaje_id>/cancelar/', views.cancelar_viaje, name='cancelar_viaje'),
    path('<int:viaje_id>/calificar/', views.calificar_viaje, name='calificar_viaje'),
    path('<int:viaje_id>/compartir/', views.compartir_viaje, name='compartir_viaje'),
    path('<int:viaje_id>/emergencia/', views.activar_emergencia, name='activar_emergencia'),
    path('seguimiento/<uuid:token>/', views.seguimiento_publico, name='seguimiento_publico'),
]
