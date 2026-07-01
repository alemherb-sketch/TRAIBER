from django import forms

from .models import Vehiculo


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = (
            'tipo_vehiculo', 'placa', 'marca', 'modelo', 'color', 'anio',
            'soat_numero', 'soat_vencimiento', 'soat_foto', 'foto_vehiculo',
        )
        widgets = {
            'soat_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'tipo_vehiculo': 'Tipo de vehículo', 'placa': 'Placa', 'marca': 'Marca',
            'modelo': 'Modelo', 'color': 'Color', 'anio': 'Año',
            'soat_numero': 'N° de póliza SOAT', 'soat_vencimiento': 'Vencimiento SOAT',
            'soat_foto': 'Foto del SOAT', 'foto_vehiculo': 'Foto del vehículo',
        }

    def clean_placa(self):
        return self.cleaned_data['placa'].upper().replace('-', '')
