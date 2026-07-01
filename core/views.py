from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def inicio(request):
    """Landing page publica de TRAIBER."""
    if request.user.is_authenticated:
        return redirect('core:redirigir_panel')
    return render(request, 'core/inicio.html')


@login_required
def redirigir_panel(request):
    """Redirige a cada usuario a su panel segun su rol."""
    usuario = request.user
    if usuario.es_admin_traiber:
        return redirect('core:panel_admin')
    if usuario.es_conductor:
        return redirect('viajes:panel_conductor')
    return redirect('viajes:panel_pasajero')


@login_required
def panel_admin(request):
    if not request.user.es_admin_traiber:
        return redirect('core:redirigir_panel')

    from usuarios.models import Usuario, PerfilConductor
    from vehiculos.models import Vehiculo
    from viajes.models import Viaje
    from soporte.models import TicketSoporte

    contexto = {
        'total_pasajeros': Usuario.objects.filter(tipo_usuario=Usuario.TipoUsuario.PASAJERO).count(),
        'total_conductores': Usuario.objects.filter(tipo_usuario=Usuario.TipoUsuario.CONDUCTOR).count(),
        'conductores_pendientes': PerfilConductor.objects.filter(
            estado_aprobacion=PerfilConductor.EstadoAprobacion.PENDIENTE
        ).select_related('usuario'),
        'vehiculos_pendientes': Vehiculo.objects.filter(aprobado=False).select_related('conductor'),
        'viajes_activos': Viaje.objects.filter(estado__in=[
            Viaje.Estado.BUSCANDO, Viaje.Estado.ACEPTADO,
            Viaje.Estado.EN_CAMINO_RECOJO, Viaje.Estado.EN_CURSO,
        ]).select_related('pasajero', 'conductor'),
        'tickets_abiertos': TicketSoporte.objects.filter(
            estado__in=[TicketSoporte.Estado.ABIERTO, TicketSoporte.Estado.EN_PROCESO]
        ).select_related('usuario'),
        'usuarios_bloqueados': Usuario.objects.filter(cuenta_bloqueada=True),
    }
    return render(request, 'core/panel_admin.html', contexto)


@login_required
def admin_aprobar_conductor(request, perfil_id):
    from usuarios.models import PerfilConductor
    if not request.user.es_admin_traiber:
        return redirect('core:redirigir_panel')
    perfil = PerfilConductor.objects.get(pk=perfil_id)
    perfil.estado_aprobacion = PerfilConductor.EstadoAprobacion.APROBADO
    perfil.save(update_fields=['estado_aprobacion'])
    return redirect('core:panel_admin')


@login_required
def admin_rechazar_conductor(request, perfil_id):
    from usuarios.models import PerfilConductor
    if not request.user.es_admin_traiber:
        return redirect('core:redirigir_panel')
    perfil = PerfilConductor.objects.get(pk=perfil_id)
    perfil.estado_aprobacion = PerfilConductor.EstadoAprobacion.RECHAZADO
    perfil.save(update_fields=['estado_aprobacion'])
    return redirect('core:panel_admin')


@login_required
def admin_aprobar_vehiculo(request, vehiculo_id):
    from vehiculos.models import Vehiculo
    if not request.user.es_admin_traiber:
        return redirect('core:redirigir_panel')
    vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
    vehiculo.aprobado = True
    vehiculo.save(update_fields=['aprobado'])
    return redirect('core:panel_admin')


@login_required
def admin_bloquear_usuario(request, usuario_id):
    from usuarios.models import Usuario
    if not request.user.es_admin_traiber:
        return redirect('core:redirigir_panel')
    usuario = Usuario.objects.get(pk=usuario_id)
    usuario.cuenta_bloqueada = not usuario.cuenta_bloqueada
    usuario.is_active = not usuario.cuenta_bloqueada
    usuario.save(update_fields=['cuenta_bloqueada', 'is_active'])
    return redirect('core:panel_admin')
