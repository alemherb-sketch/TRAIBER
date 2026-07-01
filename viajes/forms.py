from django import forms

from .models import Viaje, OfertaViaje


class SolicitarViajeForm(forms.ModelForm):
    class Meta:
        model = Viaje
        fields = (
            'origen_direccion', 'origen_lat', 'origen_lng',
            'destino_direccion', 'destino_lat', 'destino_lng',
            'distancia_km', 'tiempo_estimado_min',
            'modo_tarifa', 'tarifa_propuesta_pasajero', 'metodo_pago',
        )
        widgets = {
            'origen_lat': forms.HiddenInput(), 'origen_lng': forms.HiddenInput(),
            'destino_lat': forms.HiddenInput(), 'destino_lng': forms.HiddenInput(),
            'distancia_km': forms.HiddenInput(), 'tiempo_estimado_min': forms.HiddenInput(),
        }


class OfertaViajeForm(forms.ModelForm):
    class Meta:
        model = OfertaViaje
        fields = ('monto_ofertado',)
        labels = {'monto_ofertado': 'Tu oferta (S/)'}
