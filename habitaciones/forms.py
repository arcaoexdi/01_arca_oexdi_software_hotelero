from django import forms
from .models import Habitacion

class HabitacionForm(forms.ModelForm):
    """
    Formulario para la creación y edición de una habitación con validaciones adicionales.
    Incluye soporte para imágenes y descripción.
    """
    class Meta:
        model = Habitacion
        fields = ['numero', 'tipo', 'estado_habitacion', 'capacidad', 'precio', 'descripcion', 'imagen']
        widgets = {
            'numero': forms.TextInput(attrs={'placeholder': 'Ej: 101'}),
            'tipo': forms.Select(),
            'estado_habitacion': forms.Select(),
            'capacidad': forms.NumberInput(attrs={'min': 1}),
            'precio': forms.NumberInput(attrs={'min': 0}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción de la habitación'}),
            'imagen': forms.ClearableFileInput(),
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
