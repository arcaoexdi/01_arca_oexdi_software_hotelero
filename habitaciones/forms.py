from django import forms
from .models import Habitacion

class HabitacionForm(forms.ModelForm):
    """
    Formulario para la creación y edición de una habitación con validaciones adicionales.
    Incluye soporte para imágenes.
    """
    class Meta:
        model = Habitacion
        fields = ['numero', 'tipo', 'estado_habitacion', 'capacidad', 'precio', 'imagen']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 101'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_capacidad(self):
        capacidad = self.cleaned_data.get('capacidad')
        if capacidad < 1:
            raise forms.ValidationError("La capacidad debe ser al menos 1 huésped.")
        return capacidad

    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        qs = Habitacion.objects.filter(numero=numero)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe una habitación con este número.")
        return numero
