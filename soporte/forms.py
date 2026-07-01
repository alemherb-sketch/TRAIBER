from django import forms

from .models import TicketSoporte, MensajeSoporte


class TicketSoporteForm(forms.ModelForm):
    class Meta:
        model = TicketSoporte
        fields = ('categoria', 'viaje', 'asunto')
        labels = {'categoria': 'Categoría', 'viaje': 'Viaje relacionado (opcional)', 'asunto': 'Cuéntanos qué pasó'}
        widgets = {'asunto': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario is not None:
            from viajes.models import Viaje
            self.fields['viaje'].queryset = Viaje.objects.filter(pasajero=usuario) | Viaje.objects.filter(conductor=usuario)
            self.fields['viaje'].required = False


class MensajeSoporteForm(forms.ModelForm):
    class Meta:
        model = MensajeSoporte
        fields = ('texto',)
        labels = {'texto': ''}
        widgets = {'texto': forms.TextInput(attrs={'placeholder': 'Escribe un mensaje...', 'class': 'form-control'})}
