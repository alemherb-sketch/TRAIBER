from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('panel/', views.redirigir_panel, name='redirigir_panel'),
    path('admin-panel/', views.panel_admin, name='panel_admin'),
    path('admin-panel/conductor/<int:perfil_id>/aprobar/', views.admin_aprobar_conductor, name='admin_aprobar_conductor'),
    path('admin-panel/conductor/<int:perfil_id>/rechazar/', views.admin_rechazar_conductor, name='admin_rechazar_conductor'),
    path('admin-panel/vehiculo/<int:vehiculo_id>/aprobar/', views.admin_aprobar_vehiculo, name='admin_aprobar_vehiculo'),
    path('admin-panel/usuario/<int:usuario_id>/bloquear/', views.admin_bloquear_usuario, name='admin_bloquear_usuario'),
]
