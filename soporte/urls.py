from django.urls import path

from . import views

app_name = 'soporte'

urlpatterns = [
    path('', views.mis_tickets, name='mis_tickets'),
    path('nuevo/', views.crear_ticket, name='crear_ticket'),
    path('<int:ticket_id>/', views.ver_ticket, name='ver_ticket'),
    path('<int:ticket_id>/estado/<str:estado>/', views.cambiar_estado_ticket, name='cambiar_estado_ticket'),
]
