import datetime

from django.core.management.base import BaseCommand

from usuarios.models import Usuario, PerfilConductor
from vehiculos.models import Vehiculo


class Command(BaseCommand):
    help = 'Crea usuarios de ejemplo (un pasajero y un conductor ya aprobado) para probar TRAIBER rapidamente.'

    def handle(self, *args, **options):
        if not Usuario.objects.filter(username='pasajero_demo').exists():
            pasajero = Usuario.objects.create_user(
                username='pasajero_demo', password='Demo2026!', email='pasajero@traiber.pe',
                first_name='Rosa', last_name='Quispe', celular='987654321',
                tipo_usuario=Usuario.TipoUsuario.PASAJERO,
            )
            self.stdout.write(self.style.SUCCESS(f'Pasajero creado: {pasajero.username} / Demo2026!'))
        else:
            self.stdout.write('Pasajero demo ya existe.')

        if not Usuario.objects.filter(username='conductor_demo').exists():
            conductor = Usuario.objects.create_user(
                username='conductor_demo', password='Demo2026!', email='conductor@traiber.pe',
                first_name='Carlos', last_name='Ramirez', celular='912345678',
                tipo_usuario=Usuario.TipoUsuario.CONDUCTOR,
            )
            PerfilConductor.objects.create(
                usuario=conductor, licencia_numero='Q12345678',
                licencia_vencimiento=datetime.date.today() + datetime.timedelta(days=365),
                estado_aprobacion=PerfilConductor.EstadoAprobacion.APROBADO,
                disponible=True, latitud_actual=-12.0464, longitud_actual=-77.0428,
            )
            Vehiculo.objects.create(
                conductor=conductor, tipo_vehiculo=Vehiculo.TipoVehiculo.ECONOMICO,
                placa='ABC123', marca='Toyota', modelo='Yaris', color='Blanco', anio=2020,
                soat_numero='SOAT-001', soat_vencimiento=datetime.date.today() + datetime.timedelta(days=200),
                aprobado=True,
            )
            self.stdout.write(self.style.SUCCESS(f'Conductor creado: {conductor.username} / Demo2026!'))
        else:
            self.stdout.write('Conductor demo ya existe.')
