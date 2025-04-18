from django.utils import timezone
from django.db import models
from habitaciones.models import Habitacion


## MODELO DE HUESPEDES

class Huesped(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('Cedula de ciudadania', 'Cedula de ciudadania'),
        ('Pasaporte', 'Pasaporte'),
        ('Cedula Extranjera', 'Cedula Extranjera'),
        ('Registro civil', 'Registro civil'),
        ('Tarjeta de Identidad', 'Tarjeta de Identidad')
    ]
    
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    tipo_documento = models.CharField(
        max_length=30,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='Cedula de ciudadania'  # O cualquiera válida de la lista
    )

    numero_documento = models.CharField(max_length=50, unique=True)
    correo_electronico = models.EmailField(unique=True)  # Evita duplicados
    telefono = models.CharField(max_length=15)
    vehiculo = models.CharField(max_length=50, blank=True, null=True)
    placas = models.CharField(max_length=10, blank=True, null=True)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE, related_name='huespedes')
    fecha_entrada = models.DateField(default=timezone.now)
    fecha_salida = models.DateField()

    def __str__(self):
        return f'{self.nombre} {self.apellido}'
    


