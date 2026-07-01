from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario, PerfilConductor, ContactoConfianza


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'tipo_usuario', 'celular', 'cuenta_bloqueada', 'is_active')
    list_filter = ('tipo_usuario', 'cuenta_bloqueada', 'celular_verificado')
    fieldsets = UserAdmin.fieldsets + (
        ('Datos TRAIBER', {
            'fields': ('tipo_usuario', 'celular', 'dni', 'foto_perfil', 'celular_verificado',
                       'correo_verificado', 'cuenta_bloqueada', 'motivo_bloqueo')
        }),
    )


@admin.register(PerfilConductor)
class PerfilConductorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'estado_aprobacion', 'disponible', 'calificacion_promedio', 'total_viajes')
    list_filter = ('estado_aprobacion', 'disponible')
    actions = ['aprobar_conductores', 'rechazar_conductores']

    @admin.action(description='Aprobar conductores seleccionados')
    def aprobar_conductores(self, request, queryset):
        queryset.update(estado_aprobacion=PerfilConductor.EstadoAprobacion.APROBADO)

    @admin.action(description='Rechazar conductores seleccionados')
    def rechazar_conductores(self, request, queryset):
        queryset.update(estado_aprobacion=PerfilConductor.EstadoAprobacion.RECHAZADO)


@admin.register(ContactoConfianza)
class ContactoConfianzaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'celular', 'usuario')
