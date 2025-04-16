from django import forms
from .models import Producto, Categoria

class ProductoForm(forms.ModelForm):
    nueva_categoria = forms.CharField(
        max_length=100,
        required=False,
        label="Nueva categoría",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escribe una nueva categoría (opcional)'}),
        help_text="Si no ves tu categoría, puedes crear una nueva."
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(activo=True),  # Solo categorías activas
        empty_label="Seleccione una categoría",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Selecciona una categoría existente o crea una nueva."
    )

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'disponible', 'categoria', 'imagen']

    def clean(self):
        cleaned_data = super().clean()
        nueva_categoria = cleaned_data.get('nueva_categoria')
        
        # Si se introduce un nombre de nueva categoría, la asignamos
        if nueva_categoria:
            # Validar que no exista una categoría con ese nombre
            if Categoria.objects.filter(nombre__iexact=nueva_categoria).exists():
                raise forms.ValidationError("Ya existe una categoría con ese nombre.")
            # Crear una nueva categoría si no existe
            categoria = Categoria.objects.create(nombre=nueva_categoria)
            cleaned_data['categoria'] = categoria  # Asignamos la nueva categoría al producto
        return cleaned_data
