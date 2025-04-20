from django import forms
from .models import Consumo
from habitaciones.models import Habitacion
from django.utils.timezone import now

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

        # Filtrar habitaciones disponibles con huéspedes activos
        self.fields['habitacion'].queryset = Habitacion.objects.filter(
            estado_habitacion='disponible'
        ).exclude(
            huespedes__fecha_salida__lt=now()  # Excluye las habitaciones cuyo huésped tenga fecha de salida pasada
        ).distinct()
        
         # ✅ Mostrar como "Habitación #101", etc.
        self.fields['habitacion'].label_from_instance = lambda obj: f'Habitación #{obj.numero}'


        # Etiquetas personalizadas
        self.fields['habitacion'].label = 'Habitación'
        self.fields['huesped'].label = 'Huésped'
        self.fields['producto'].label = 'Producto'
        self.fields['cantidad'].label = 'Cantidad'
        self.fields['observaciones'].label = 'Observaciones'

        # Clases para los campos
        self.fields['habitacion'].widget.attrs.update({'class': 'form-control shadow-sm'})
        self.fields['huesped'].widget.attrs.update({'class': 'form-control shadow-sm'})
        self.fields['producto'].widget.attrs.update({'class': 'form-control shadow-sm'})

    def clean(self):
        cleaned_data = super().clean()
        habitacion = cleaned_data.get('habitacion')
        huesped = cleaned_data.get('huesped')
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')

        # Validación de si el huésped pertenece a la habitación seleccionada
        if habitacion and huesped:
            if huesped.habitacion != habitacion:
                raise forms.ValidationError("Este huésped no pertenece a la habitación seleccionada.")
        
        # Validación de stock
        if producto and cantidad > producto.disponible:
            raise forms.ValidationError({'cantidad': "No hay suficiente stock del producto."})

        return cleaned_data

    def save(self, commit=True):
        consumo = super().save(commit=False)

        # Actualización del precio total antes de guardar el consumo
        consumo.precio_total = consumo.total()  # Asegúrate de tener un método `total` en el modelo Consumo que calcule el precio total

        if commit:
            consumo.save()

            # Actualización del stock del producto
            if consumo.producto:
                consumo.producto.disponible -= consumo.cantidad
                consumo.producto.save()

        return consumo
