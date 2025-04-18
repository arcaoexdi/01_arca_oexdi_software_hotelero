from django.db import models
from django.apps import apps
from django.core.validators import MinValueValidator

class Habitacion(models.Model):
    TIPOS_HABITACION = [
        ('familiar', 'Familiar'),
        ('pareja', 'Pareja'),
        ('suite', 'Suite'),
        ('individual', 'Individual'),
    ]

    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('reservada', 'Reservada'),
        ('ocupada', 'Ocupada'),
        ('aseo', 'En Aseo'),
        ('mantenimiento', 'En Mantenimiento'),
    ]

    numero = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Número de Habitación"
    )

    estado_habitacion = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='disponible',
        verbose_name="Estado de la Habitación",
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_HABITACION,
        verbose_name="Tipo de Habitación"
    )

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio por Noche"
    )

    capacidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Capacidad Máxima"
    )

    imagen = models.ImageField(
        upload_to='habitaciones/', null=True, blank=True
    )

    class Meta:
        ordering = ['numero']
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"

    def __str__(self):
        return f"Habitación {self.numero} - {self.get_tipo_display()} ({self.get_estado_display()})"

    def obtener_huespedes(self):
        Huesped = apps.get_model('huespedes', 'Huesped')
        return list(Huesped.objects.filter(habitacion=self))

    @property
    def capacidad_actual(self):
        return len(self.obtener_huespedes())

    def esta_disponible(self):
        if self.estado == 'disponible' and self.capacidad_actual < self.capacidad:
            return True
        else:
            if self.capacidad_actual >= self.capacidad:
                self.estado = 'ocupada'
                self.save()
            return False

    def esta_llena(self):
        return self.capacidad_actual >= self.capacidad

    def actualizar_estado(self):
        if self.capacidad_actual >= self.capacidad:
            self.estado = 'ocupada'
        elif self.capacidad_actual == 0:
            self.estado = 'disponible'
        else:
            self.estado = 'disponible'  # Podrías añadir "parcialmente ocupada" si algún día lo necesitás
        self.save()
