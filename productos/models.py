from django.db import models
from django.core.exceptions import ValidationError

class Categoria(models.Model):
    """
    Modelo para representar las categorías de productos.
    Cada categoría puede tener múltiples productos asociados.
    """
    nombre = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Nombre de la categoría"
    )
    descripcion = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Descripción de la categoría"
    )
    activo = models.BooleanField(
        default=True, 
        verbose_name="Activo", 
        help_text="Indica si la categoría está activa o no."
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']


class Producto(models.Model):
    """
    Modelo para representar los productos disponibles para la venta.
    """
    nombre = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Nombre del producto", 
        help_text="Nombre único para identificar el producto."
    )
    descripcion = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Descripción", 
        help_text="Descripción opcional del producto."
    )
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Precio",
        help_text="El precio debe ser un valor positivo, en formato decimal."
    )
    disponible = models.BooleanField(
        default=True, 
        verbose_name="Disponible",
        help_text="Indica si el producto está disponible para la venta."
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de creación", 
        help_text="Fecha en la que se creó el producto."
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True, 
        verbose_name="Última actualización", 
        help_text="Fecha en la que se realizó la última actualización del producto."
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Categoría",
        related_name="productos",
        help_text="Categoría opcional para organizar los productos."
    )
    imagen = models.ImageField(
        upload_to='productos/',
        null=True,
        blank=True,
        verbose_name="Imagen del producto",
        help_text="Imagen representativa del producto (opcional)."
    )

    def __str__(self):
        return f"{self.nombre} - ${self.precio:.2f}"

    def clean(self):
        """
        Validaciones personalizadas para el modelo Producto.
        """
        super().clean()
        if self.precio is None:
            raise ValidationError({'precio': "El precio es obligatorio."})
        if self.precio <= 0:
            raise ValidationError({'precio': "El precio debe ser mayor a 0."})
        if self.nombre and len(self.nombre.strip()) < 3:
            raise ValidationError({'nombre': "El nombre del producto debe tener al menos 3 caracteres."})

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['categoria']),
        ]


