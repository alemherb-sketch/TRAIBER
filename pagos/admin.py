from django.contrib import admin

from .models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('viaje', 'metodo', 'monto', 'estado', 'creado')
    list_filter = ('metodo', 'estado')
