from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from calificaciones.models import Calificacion
from pagos.models import Pago
from usuarios.models import PerfilConductor
from vehiculos.models import Vehiculo
from .forms import SolicitarViajeForm, OfertaViajeForm
from .models import Viaje, OfertaViaje, CompartirViaje
from . import notificaciones


def calcular_tarifa_sugerida(distancia_km, tiempo_estimado_min):
    tarifa = (
        settings.TARIFA_BASE
        + float(distancia_km) * settings.TARIFA_POR_KM
        + float(tiempo_estimado_min) * settings.TARIFA_POR_MINUTO
    )
    return round(max(tarifa, settings.TARIFA_MINIMA), 2)


def _asignar_conductor(viaje, conductor, tarifa_final):
    vehiculo = getattr(conductor, 'vehiculo', None)
    viaje.conductor = conductor
    viaje.tarifa_final = tarifa_final
    viaje.estado = Viaje.Estado.ACEPTADO
    viaje.hora_aceptado = timezone.now()
    if vehiculo:
        viaje.placa_vehiculo = vehiculo.placa
        viaje.modelo_vehiculo = f'{vehiculo.marca} {vehiculo.modelo}'
        viaje.color_vehiculo = vehiculo.color
    viaje.save()

    notificaciones.notificar_estado_viaje(viaje.id, viaje.estado, 'Un conductor aceptó tu viaje.')
    notificaciones.notificar_solicitud_tomada(viaje.id)


# ---------- Vistas del pasajero ----------

@login_required
def panel_pasajero(request):
    if not request.user.es_pasajero:
        return redirect('core:redirigir_panel')

    viaje_activo = Viaje.objects.filter(pasajero=request.user).exclude(
        estado__in=[Viaje.Estado.FINALIZADO, Viaje.Estado.CANCELADO]
    ).first()
    if viaje_activo:
        return redirect('viajes:ver_viaje', viaje_id=viaje_activo.id)

    form = SolicitarViajeForm()
    return render(request, 'viajes/panel_pasajero.html', {
        'form': form,
        'tarifa_base': settings.TARIFA_BASE,
        'tarifa_por_km': settings.TARIFA_POR_KM,
        'tarifa_por_minuto': settings.TARIFA_POR_MINUTO,
        'tarifa_minima': settings.TARIFA_MINIMA,
    })


@login_required
def solicitar_viaje(request):
    if not request.user.es_pasajero or request.method != 'POST':
        return redirect('core:redirigir_panel')

    form = SolicitarViajeForm(request.POST)
    if form.is_valid():
        viaje = form.save(commit=False)
        viaje.pasajero = request.user
        viaje.tarifa_sugerida = calcular_tarifa_sugerida(viaje.distancia_km, viaje.tiempo_estimado_min)
        viaje.save()
        notificaciones.notificar_nueva_solicitud_a_conductores(viaje.id)
        messages.success(request, 'Buscando un conductor disponible para tu viaje...')
        return redirect('viajes:ver_viaje', viaje_id=viaje.id)

    messages.error(request, 'Revisa los datos de origen y destino e intenta nuevamente.')
    return redirect('viajes:panel_pasajero')


@login_required
def ver_viaje(request, viaje_id):
    viaje = get_object_or_404(Viaje, pk=viaje_id)
    if request.user not in (viaje.pasajero, viaje.conductor) and not request.user.es_admin_traiber:
        return redirect('core:redirigir_panel')

    ofertas = viaje.ofertas.select_related('conductor').filter(estado=OfertaViaje.Estado.PENDIENTE) \
        if viaje.modo_tarifa == Viaje.ModoTarifa.OFERTA else []

    ya_califico = False
    if viaje.estado == Viaje.Estado.FINALIZADO:
        ya_califico = Calificacion.objects.filter(viaje=viaje, autor=request.user).exists()

    enlace_compartir = getattr(viaje, 'compartir', None)

    return render(request, 'viajes/ver_viaje.html', {
        'viaje': viaje,
        'ofertas': ofertas,
        'es_pasajero_de_este_viaje': request.user == viaje.pasajero,
        'es_conductor_de_este_viaje': request.user == viaje.conductor,
        'ya_califico': ya_califico,
        'enlace_compartir': enlace_compartir,
        'numero_emergencia': settings.NUMERO_EMERGENCIA_PERU,
    })


@login_required
def cancelar_viaje(request, viaje_id):
    viaje = get_object_or_404(Viaje, pk=viaje_id)
    if request.user not in (viaje.pasajero, viaje.conductor):
        return redirect('core:redirigir_panel')

    viaje.estado = Viaje.Estado.CANCELADO
    viaje.motivo_cancelacion = request.POST.get('motivo', 'Cancelado por el usuario')
    viaje.save(update_fields=['estado', 'motivo_cancelacion'])
    notificaciones.notificar_estado_viaje(viaje.id, viaje.estado, 'El viaje fue cancelado.')
    notificaciones.notificar_solicitud_tomada(viaje.id)
    messages.info(request, 'El viaje fue cancelado.')
    return redirect('core:redirigir_panel')


@login_required
def aceptar_oferta(request, oferta_id):
    oferta = get_object_or_404(OfertaViaje, pk=oferta_id)
    viaje = oferta.viaje
    if request.user != viaje.pasajero:
        return redirect('core:redirigir_panel')

    oferta.estado = OfertaViaje.Estado.ACEPTADA
    oferta.save(update_fields=['estado'])
    viaje.ofertas.exclude(pk=oferta.id).update(estado=OfertaViaje.Estado.RECHAZADA)

    _asignar_conductor(viaje, oferta.conductor, oferta.monto_ofertado)
    notificaciones.notificar_oferta_respondida(oferta.conductor_id, viaje.id, 'aceptada')
    for otra in viaje.ofertas.exclude(pk=oferta.id):
        notificaciones.notificar_oferta_respondida(otra.conductor_id, viaje.id, 'rechazada')

    messages.success(request, 'Aceptaste la oferta del conductor.')
    return redirect('viajes:ver_viaje', viaje_id=viaje.id)


@login_required
def historial_pasajero(request):
    if not request.user.es_pasajero:
        return redirect('core:redirigir_panel')
    viajes = Viaje.objects.filter(pasajero=request.user, estado__in=[Viaje.Estado.FINALIZADO, Viaje.Estado.CANCELADO])
    return render(request, 'viajes/historial_pasajero.html', {'viajes': viajes})


# ---------- Vistas del conductor ----------

@login_required
def panel_conductor(request):
    if not request.user.es_conductor:
        return redirect('core:redirigir_panel')

    perfil, _ = PerfilConductor.objects.get_or_create(usuario=request.user)
    vehiculo = Vehiculo.objects.filter(conductor=request.user).first()

    viaje_activo = Viaje.objects.filter(conductor=request.user).exclude(
        estado__in=[Viaje.Estado.FINALIZADO, Viaje.Estado.CANCELADO]
    ).first()
    if viaje_activo:
        return redirect('viajes:ver_viaje', viaje_id=viaje_activo.id)

    solicitudes = []
    if perfil.aprobado and vehiculo and vehiculo.aprobado and perfil.disponible:
        solicitudes = Viaje.objects.filter(estado=Viaje.Estado.BUSCANDO).exclude(
            modo_tarifa=Viaje.ModoTarifa.OFERTA, ofertas__conductor=request.user
        )

    ganancias_totales = Viaje.objects.filter(
        conductor=request.user, estado=Viaje.Estado.FINALIZADO
    )
    total_ganado = sum(v.monto_neto_conductor for v in ganancias_totales)

    return render(request, 'viajes/panel_conductor.html', {
        'perfil': perfil,
        'vehiculo': vehiculo,
        'solicitudes': solicitudes,
        'total_ganado': total_ganado,
        'total_viajes': ganancias_totales.count(),
    })


@login_required
def actualizar_disponibilidad(request):
    if not request.user.es_conductor or request.method != 'POST':
        return redirect('core:redirigir_panel')

    perfil, _ = PerfilConductor.objects.get_or_create(usuario=request.user)
    vehiculo = Vehiculo.objects.filter(conductor=request.user).first()

    if not perfil.aprobado or not vehiculo or not vehiculo.aprobado:
        messages.error(request, 'Tu cuenta o vehículo aún no ha sido aprobado por el administrador.')
        return redirect('viajes:panel_conductor')

    perfil.disponible = not perfil.disponible
    perfil.save(update_fields=['disponible'])
    return redirect('viajes:panel_conductor')


@login_required
def actualizar_ubicacion_conductor(request):
    if not request.user.es_conductor or request.method != 'POST':
        return JsonResponse({'ok': False}, status=403)

    lat = request.POST.get('lat')
    lng = request.POST.get('lng')
    PerfilConductor.objects.filter(usuario=request.user).update(
        latitud_actual=lat, longitud_actual=lng, ultima_actualizacion_ubicacion=timezone.now()
    )
    return JsonResponse({'ok': True})


@login_required
def solicitudes_json(request):
    """Fallback por polling ademas del WebSocket, util si el navegador bloquea WS."""
    if not request.user.es_conductor:
        return JsonResponse({'solicitudes': []})
    perfil = getattr(request.user, 'perfil_conductor', None)
    if not perfil or not perfil.disponible:
        return JsonResponse({'solicitudes': []})

    solicitudes = Viaje.objects.filter(estado=Viaje.Estado.BUSCANDO).exclude(
        modo_tarifa=Viaje.ModoTarifa.OFERTA, ofertas__conductor=request.user
    ).values('id', 'origen_direccion', 'destino_direccion', 'distancia_km', 'tarifa_sugerida', 'modo_tarifa')
    return JsonResponse({'solicitudes': list(solicitudes)})


@login_required
def aceptar_viaje(request, viaje_id):
    viaje = get_object_or_404(Viaje, pk=viaje_id)
    if not request.user.es_conductor or viaje.estado != Viaje.Estado.BUSCANDO:
        messages.error(request, 'Este viaje ya no está disponible.')
        return redirect('viajes:panel_conductor')

    _asignar_conductor(viaje, request.user, viaje.tarifa_sugerida)
    messages.success(request, 'Aceptaste el viaje.')
    return redirect('viajes:ver_viaje', viaje_id=viaje.id)


@login_required
def ofertar_viaje(request, viaje_id):
    viaje = get_object_or_404(Viaje, pk=viaje_id)
    if not request.user.es_conductor or request.method != 'POST':
        return redirect('viajes:panel_conductor')

    form = OfertaViajeForm(request.POST)
    if form.is_valid():
        oferta, creada = OfertaViaje.objects.update_or_create(
            viaje=viaje, conductor=request.user,
            defaults={'monto_ofertado': form.cleaned_data['monto_ofertado'], 'estado': OfertaViaje.Estado.PENDIENTE}
        )
        notificaciones.notificar_oferta_viaje(viaje.id, oferta)
        messages.success(request, 'Tu oferta fue enviada al pasajero.')
    return redirect('viajes:panel_conductor')


@login_required
def iniciar_viaje(request, viaje_id):
    viaje = get_object_or_404(Viaje, pk=viaje_id)
    if request.user != viaje.conductor:
        return redirect('core:redirigir_panel')

    viaje.estado = Viaje.Estado.EN_CURSO
    viaje.hora_inicio = timezone.now()
    viaje.save(update_fields=['estado', 'hora_inicio'])
    notificaciones.notificar_estado_viaje(viaje.id, viaje.estado, 'El viaje ha comenzado.')
    return redirect('viajes:ver_viaje', viaje_id=viaje.id)


@login_required
def finalizar_viaje(request, viaje_id):
    viaje = get_object_or_404(Viaje, pk=viaje_id)
    if request.user != viaje.conductor:
        return redirect('core:redirigir_panel')

    viaje.estado = Viaje.Estado.FINALIZADO
    viaje.hora_fin = timezone.now()
    if not viaje.tarifa_final:
        viaje.tarifa_final = viaje.tarifa_sugerida
    viaje.save(update_fields=['estado', 'hora_fin', 'tarifa_final'])

    pago, _ = Pago.objects.get_or_create(
        viaje=viaje, defaults={'metodo': viaje.metodo_pago, 'monto': viaje.tarifa_final + viaje.propina}
    )
    pago.marcar_pagado()

    perfil = getattr(request.user, 'perfil_conductor', None)
    if perfil:
        perfil.total_viajes += 1
        perfil.saldo_ganancias += Decimal(str(viaje.monto_neto_conductor))
        perfil.save(update_fields=['total_viajes', 'saldo_ganancias'])

    notificaciones.notificar_estado_viaje(viaje.id, viaje.estado, 'El viaje ha finalizado. ¡Gracias por usar TRAIBER!')
    messages.success(request, 'Viaje finalizado y pago registrado.')
    return redirect('viajes:ver_viaje', viaje_id=viaje.id)


@login_required
def historial_conductor(request):
    if not request.user.es_conductor:
        return redirect('core:redirigir_panel')
    viajes = Viaje.objects.filter(conductor=request.user, estado__in=[Viaje.Estado.FINALIZADO, Viaje.Estado.CANCELADO])
    return render(request, 'viajes/historial_conductor.html', {'viajes': viajes})


# ---------- Calificaciones ----------

@login_required
def calificar_viaje(request, viaje_id):
    viaje = get_object_or_404(Viaje, pk=viaje_id)
    if request.user not in (viaje.pasajero, viaje.conductor) or request.method != 'POST':
        return redirect('core:redirigir_panel')

    receptor = viaje.conductor if request.user == viaje.pasajero else viaje.pasajero
    if receptor:
        Calificacion.objects.get_or_create(
            viaje=viaje, autor=request.user,
            defaults={
                'receptor': receptor,
                'puntuacion': request.POST.get('puntuacion', 5),
                'comentario': request.POST.get('comentario', ''),
            }
        )
        messages.success(request, '¡Gracias por tu calificación!')
    return redirect('viajes:ver_viaje', viaje_id=viaje.id)


# ---------- Compartir viaje / emergencia ----------

@login_required
def compartir_viaje(request, viaje_id):
    viaje = get_object_or_404(Viaje, pk=viaje_id)
    if request.user != viaje.pasajero:
        return redirect('core:redirigir_panel')
    CompartirViaje.objects.get_or_create(viaje=viaje)
    return redirect('viajes:ver_viaje', viaje_id=viaje.id)


def seguimiento_publico(request, token):
    enlace = get_object_or_404(CompartirViaje, token=token, activo=True)
    return render(request, 'viajes/seguimiento_publico.html', {'viaje': enlace.viaje, 'token': token})


@login_required
def activar_emergencia(request, viaje_id):
    viaje = get_object_or_404(Viaje, pk=viaje_id)
    if request.user not in (viaje.pasajero, viaje.conductor) or request.method != 'POST':
        return JsonResponse({'ok': False}, status=403)
    viaje.emergencia_activada = True
    viaje.save(update_fields=['emergencia_activada'])
    notificaciones.notificar_estado_viaje(viaje.id, viaje.estado, 'BOTÓN DE EMERGENCIA ACTIVADO')
    return JsonResponse({'ok': True})
