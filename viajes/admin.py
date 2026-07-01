from django.contrib import admin

from .models import Viaje, OfertaViaje, CompartirViaje


class OfertaViajeInline(admin.TabularInline):
    model = OfertaViaje
    extra = 0


@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ('id', 'pasajero', 'conductor', 'estado', 'tarifa_final', 'emergencia_activada', 'creado')
    list_filter = ('estado', 'modo_tarifa', 'emergencia_activada')
    search_fields = ('origen_direccion', 'destino_direccion', 'pasajero__username', 'conductor__username')
    inlines = [OfertaViajeInline]


@admin.register(CompartirViaje)
class CompartirViajeAdmin(admin.ModelAdmin):
    list_display = ('viaje', 'token', 'activo')
