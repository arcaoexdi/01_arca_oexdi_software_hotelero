from django import forms
from .models import Consumo
from habitaciones.models import Habitacion
from django.utils.timezone import now


# FORM DE CONSUMOS 
class ConsumoForm(forms.ModelForm):
    class Meta:
        model = Consumo
        fields = ['habitacion', 'huesped', 'producto', 'cantidad', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Opcional: detalles sobre el consumo...',
                'class': 'form-control shadow-sm'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control shadow-sm',
                'min': '1'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Solo habitaciones disponibles
        self.fields['habitacion'].queryset = Habitacion.objects.filter(estado='disponible')

        # Etiquetas personalizadas si las necesitas
        self.fields['habitacion'].label = 'Habitación'
        self.fields['huesped'].label = 'Huésped'
        self.fields['producto'].label = 'Producto'
        self.fields['cantidad'].label = 'Cantidad'
        self.fields['observaciones'].label = 'Observaciones'

        # Clases para los campos
        self.fields['habitacion'].queryset = Habitacion.objects.filter(huesped__fecha_salida__gte=now()).distinct()
        self.fields['huesped'].widget.attrs.update({'class': 'form-control shadow-sm'})
        self.fields['producto'].widget.attrs.update({'class': 'form-control shadow-sm'})

    def clean(self):
        cleaned_data = super().clean()
        habitacion = cleaned_data.get('habitacion')
        huesped = cleaned_data.get('huesped')

        if habitacion and huesped and huesped.habitacion != habitacion:
            raise forms.ValidationError("Este huésped no pertenece a la habitación seleccionada.")
        
        return cleaned_data
