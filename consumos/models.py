from django.db import models
from django.forms import ValidationError
from habitaciones.models import Habitacion
from huespedes.models import Huesped
from django.core.validators import MinValueValidator
from productos.models import Producto

from rest_framework import viewsets
from .serializers import HuespedSerializer

class HuespedViewSet(viewsets.ModelViewSet):
    queryset = Huesped.objects.all()
    serializer_class = HuespedSerializer


class Consumo(models.Model):
    """
    Modelo para representar el consumo de productos en una habitación por un huésped.
    """
    habitacion = models.ForeignKey(
        Habitacion, 
        on_delete=models.CASCADE, 
        related_name='consumos', 
        verbose_name="Habitación"
    )

    huesped = models.ForeignKey(
        Huesped, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='consumos', 
        verbose_name="Huésped (opcional)"
    )

    producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE, 
        verbose_name="Producto"
    )

    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)], 
        verbose_name="Cantidad"
    )

    fecha_consumo = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha del Consumo"
    )

    observaciones = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Observaciones"
    )

    # Campo calculado para el total del consumo, opcional
    precio_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Total del Consumo"
    )

    class Meta:
        verbose_name = "Consumo"
        verbose_name_plural = "Consumos"
        ordering = ['-fecha_consumo']

    def total(self):
        """
        Calcula el total del consumo basado en la cantidad y el precio unitario del producto.
        """
        return self.cantidad * self.producto.precio_unitario

    def save(self, *args, **kwargs):
        """
        Sobreescribir el método save para calcular el precio total antes de guardar el objeto
        y actualizar el stock del producto, si la instancia es nueva.

        Nota: Esta lógica actualiza el stock solo en la creación de un consumo.
        Si se permiten ediciones o eliminaciones, se debe complementar esta lógica.
        """
        if not self.pk:  # Si es una nueva instancia
            self.precio_total = self.total()
            # Supone que el campo 'disponible' en Producto es numérico y representa el stock
            self.producto.disponible -= self.cantidad
            self.producto.save()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Representación del consumo: producto, cantidad, habitación y, si aplica, el huésped.
        """
        return f"{self.producto.nombre} x{self.cantidad} en Habitación {self.habitacion.numero}" + (
            f" (Huésped: {self.huesped})" if self.huesped else ""
        )

    def clean(self):
        """
        Validación personalizada para asegurar que la cantidad consumida no supere el stock disponible.
        """
        super().clean()
        if self.producto and self.cantidad > self.producto.disponible:
            raise ValidationError({'cantidad': "No hay suficiente stock del producto."})
