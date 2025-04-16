from django import forms
from .models import Huesped

class HuespedForm(forms.ModelForm):
    class Meta:
        model = Huesped
        fields = [
            'nombre', 'apellido', 'tipo_documento',
            'numero_documento', 'correo_electronico',
            'telefono', 'vehiculo', 'placas'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'vehiculo': forms.TextInput(attrs={'class': 'form-control'}),
            'placas': forms.TextInput(attrs={'class': 'form-control text-uppercase'}),
        }

    def clean_placas(self):
        placas = self.cleaned_data.get('placas')
        vehiculo = self.cleaned_data.get('vehiculo')

        if vehiculo and not placas:
            raise forms.ValidationError('Debes ingresar las placas del vehículo.')

        if placas and not vehiculo:
            raise forms.ValidationError('Debes ingresar el tipo de vehículo si proporcionaste placas.')

        return placas.upper() if placas else placas

    def clean_numero_documento(self):
        return self.cleaned_data.get('numero_documento').strip()

    def clean_correo_electronico(self):
        correo = self.cleaned_data.get('correo_electronico')
        if correo:
            correo = correo.strip().lower()
            qs = Huesped.objects.filter(correo_electronico=correo)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe un huésped con este correo electrónico.')
        return correo
