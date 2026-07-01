from django.contrib.auth import login as auth_login, logout as auth_login_out
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import redirect, render

from vehiculos.forms import VehiculoForm
from vehiculos.models import Vehiculo
from .forms import RegistroPasajeroForm, RegistroConductorForm, PerfilUsuarioForm, ContactoConfianzaForm
from .models import ContactoConfianza


def elegir_rol_registro(request):
    return render(request, 'usuarios/elegir_rol.html')


def registro_pasajero(request):
    if request.method == 'POST':
        form = RegistroPasajeroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            auth_login(request, usuario)
            messages.success(request, '¡Bienvenido a TRAIBER! Tu cuenta de pasajero fue creada.')
            return redirect('core:redirigir_panel')
    else:
        form = RegistroPasajeroForm()
    return render(request, 'usuarios/registro_pasajero.html', {'form': form})


def registro_conductor(request):
    if request.method == 'POST':
        form = RegistroConductorForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            auth_login(request, usuario)
            messages.success(
                request,
                'Cuenta de conductor creada. Ahora registra los datos de tu vehículo para completar tu perfil.'
            )
            return redirect('usuarios:registrar_vehiculo')
    else:
        form = RegistroConductorForm()
    return render(request, 'usuarios/registro_conductor.html', {'form': form})


class IniciarSesionView(LoginView):
    template_name = 'usuarios/iniciar_sesion.html'
    redirect_authenticated_user = True


@login_required
def cerrar_sesion(request):
    auth_login_out(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('core:inicio')


@login_required
def registrar_vehiculo(request):
    if not request.user.es_conductor:
        return redirect('core:redirigir_panel')

    vehiculo = Vehiculo.objects.filter(conductor=request.user).first()
    if request.method == 'POST':
        form = VehiculoForm(request.POST, request.FILES, instance=vehiculo)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.conductor = request.user
            vehiculo.aprobado = False
            vehiculo.save()
            messages.success(request, 'Datos del vehículo guardados. Un administrador revisará tus documentos.')
            return redirect('core:redirigir_panel')
    else:
        form = VehiculoForm(instance=vehiculo)
    return render(request, 'usuarios/registrar_vehiculo.html', {'form': form})


@login_required
def mi_perfil(request):
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuarios:mi_perfil')
    else:
        form = PerfilUsuarioForm(instance=request.user)

    contactos = ContactoConfianza.objects.filter(usuario=request.user)
    contacto_form = ContactoConfianzaForm()
    return render(request, 'usuarios/mi_perfil.html', {
        'form': form, 'contactos': contactos, 'contacto_form': contacto_form,
    })


@login_required
def agregar_contacto_confianza(request):
    if request.method == 'POST':
        form = ContactoConfianzaForm(request.POST)
        if form.is_valid():
            contacto = form.save(commit=False)
            contacto.usuario = request.user
            contacto.save()
            messages.success(request, 'Contacto de confianza agregado.')
    return redirect('usuarios:mi_perfil')


@login_required
def eliminar_contacto_confianza(request, contacto_id):
    ContactoConfianza.objects.filter(pk=contacto_id, usuario=request.user).delete()
    return redirect('usuarios:mi_perfil')
