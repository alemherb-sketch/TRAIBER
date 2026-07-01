from django.contrib import admin

from .models import Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'conductor', 'marca', 'modelo', 'tipo_vehiculo', 'aprobado', 'soat_vigente')
    list_filter = ('aprobado', 'tipo_vehiculo')
    search_fields = ('placa', 'conductor__username', 'conductor__first_name', 'conductor__last_name')
    actions = ['aprobar_vehiculos']

    @admin.action(description='Aprobar vehículos seleccionados')
    def aprobar_vehiculos(self, request, queryset):
        queryset.update(aprobado=True)
