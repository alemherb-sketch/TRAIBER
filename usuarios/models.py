from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


validador_celular = RegexValidator(
    regex=r'^9\d{8}$',
    message='Ingresa un numero de celular peruano valido (9 digitos, empieza con 9).'
)


class Usuario(AbstractUser):
    """Usuario base de TRAIBER. Puede ser pasajero, conductor o administrador."""

    class TipoUsuario(models.TextChoices):
        PASAJERO = 'pasajero', 'Pasajero'
        CONDUCTOR = 'conductor', 'Conductor'
        ADMIN = 'admin', 'Administrador'

    tipo_usuario = models.CharField(
        max_length=15, choices=TipoUsuario.choices, default=TipoUsuario.PASAJERO
    )
    celular = models.CharField(
        max_length=9, validators=[validador_celular], blank=True,
        help_text='Numero de celular peruano (9 digitos).'
    )
    dni = models.CharField(max_length=8, blank=True, verbose_name='DNI')
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    celular_verificado = models.BooleanField(default=False)
    correo_verificado = models.BooleanField(default=False)
    cuenta_bloqueada = models.BooleanField(default=False)
    motivo_bloqueo = models.CharField(max_length=255, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_tipo_usuario_display()})'

    @property
    def es_pasajero(self):
        return self.tipo_usuario == self.TipoUsuario.PASAJERO

    @property
    def es_conductor(self):
        return self.tipo_usuario == self.TipoUsuario.CONDUCTOR

    @property
    def es_admin_traiber(self):
        return self.tipo_usuario == self.TipoUsuario.ADMIN or self.is_superuser


class PerfilConductor(models.Model):
    """Datos especificos del conductor: documentos, disponibilidad y ubicacion actual."""

    class EstadoAprobacion(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente de revision'
        APROBADO = 'aprobado', 'Aprobado'
        RECHAZADO = 'rechazado', 'Rechazado'

    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='perfil_conductor'
    )
    licencia_numero = models.CharField(max_length=20, verbose_name='N° de licencia de conducir')
    licencia_foto = models.ImageField(upload_to='documentos/licencias/', blank=True, null=True)
    licencia_vencimiento = models.DateField(null=True, blank=True)
    antecedentes_foto = models.ImageField(
        upload_to='documentos/antecedentes/', blank=True, null=True,
        verbose_name='Certificado de antecedentes penales/policiales'
    )
    estado_aprobacion = models.CharField(
        max_length=15, choices=EstadoAprobacion.choices, default=EstadoAprobacion.PENDIENTE
    )
    disponible = models.BooleanField(default=False, help_text='El conductor esta en linea y disponible')
    latitud_actual = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud_actual = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    ultima_actualizacion_ubicacion = models.DateTimeField(null=True, blank=True)
    calificacion_promedio = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    total_viajes = models.PositiveIntegerField(default=0)
    saldo_ganancias = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'Conductor: {self.usuario.get_full_name() or self.usuario.username}'

    @property
    def aprobado(self):
        return self.estado_aprobacion == self.EstadoAprobacion.APROBADO


class ContactoConfianza(models.Model):
    """Contactos a los que se puede compartir el viaje en curso (boton de emergencia)."""

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='contactos_confianza')
    nombre = models.CharField(max_length=100)
    celular = models.CharField(max_length=9, validators=[validador_celular])

    class Meta:
        verbose_name = 'Contacto de confianza'
        verbose_name_plural = 'Contactos de confianza'

    def __str__(self):
        return f'{self.nombre} ({self.celular}) - {self.usuario.username}'
