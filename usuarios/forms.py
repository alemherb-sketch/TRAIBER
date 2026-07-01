from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario, PerfilConductor, ContactoConfianza


class RegistroPasajeroForm(UserCreationForm):
    first_name = forms.CharField(label='Nombres', max_length=150)
    last_name = forms.CharField(label='Apellidos', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    celular = forms.CharField(label='Celular', max_length=9, help_text='9 dígitos, ej: 987654321')
    dni = forms.CharField(label='DNI', max_length=8, required=False)

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'celular', 'dni', 'password1', 'password2')
        labels = {'username': 'Nombre de usuario'}

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.tipo_usuario = Usuario.TipoUsuario.PASAJERO
        usuario.email = self.cleaned_data['email']
        usuario.celular = self.cleaned_data['celular']
        usuario.dni = self.cleaned_data.get('dni', '')
        if commit:
            usuario.save()
        return usuario


class RegistroConductorForm(UserCreationForm):
    first_name = forms.CharField(label='Nombres', max_length=150)
    last_name = forms.CharField(label='Apellidos', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    celular = forms.CharField(label='Celular', max_length=9, help_text='9 dígitos, ej: 987654321')
    dni = forms.CharField(label='DNI', max_length=8)
    licencia_numero = forms.CharField(label='N° de licencia de conducir', max_length=20)
    licencia_vencimiento = forms.DateField(
        label='Vencimiento de licencia', widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'celular', 'dni', 'password1', 'password2')
        labels = {'username': 'Nombre de usuario'}

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.tipo_usuario = Usuario.TipoUsuario.CONDUCTOR
        usuario.email = self.cleaned_data['email']
        usuario.celular = self.cleaned_data['celular']
        usuario.dni = self.cleaned_data['dni']
        if commit:
            usuario.save()
            PerfilConductor.objects.create(
                usuario=usuario,
                licencia_numero=self.cleaned_data['licencia_numero'],
                licencia_vencimiento=self.cleaned_data['licencia_vencimiento'],
            )
        return usuario


class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'celular', 'foto_perfil')
        labels = {
            'first_name': 'Nombres', 'last_name': 'Apellidos',
            'email': 'Correo electrónico', 'celular': 'Celular', 'foto_perfil': 'Foto de perfil',
        }


class ContactoConfianzaForm(forms.ModelForm):
    class Meta:
        model = ContactoConfianza
        fields = ('nombre', 'celular')
        labels = {'nombre': 'Nombre del contacto', 'celular': 'Celular'}
