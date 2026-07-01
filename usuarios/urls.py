from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.elegir_rol_registro, name='elegir_rol_registro'),
    path('registro/pasajero/', views.registro_pasajero, name='registro_pasajero'),
    path('registro/conductor/', views.registro_conductor, name='registro_conductor'),
    path('vehiculo/', views.registrar_vehiculo, name='registrar_vehiculo'),
    path('iniciar-sesion/', views.IniciarSesionView.as_view(), name='iniciar_sesion'),
    path('cerrar-sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('perfil/contactos/agregar/', views.agregar_contacto_confianza, name='agregar_contacto_confianza'),
    path('perfil/contactos/<int:contacto_id>/eliminar/', views.eliminar_contacto_confianza, name='eliminar_contacto_confianza'),
    path(
        'cambiar-clave/',
        auth_views.PasswordChangeView.as_view(template_name='usuarios/cambiar_clave.html'),
        name='cambiar_clave',
    ),
    path(
        'cambiar-clave/hecho/',
        auth_views.PasswordChangeDoneView.as_view(template_name='usuarios/cambiar_clave_hecho.html'),
        name='password_change_done',
    ),
]
