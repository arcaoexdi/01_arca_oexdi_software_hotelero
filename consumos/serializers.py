from django.apps import apps
from rest_framework import serializers

class HuespedSerializer(serializers.ModelSerializer):
    class Meta:
        # Establecer un modelo vacío primero
        model = None  
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar el modelo correctamente cuando se inicializa el serializador
        self.Meta.model = apps.get_model('consumos', 'Consumo')
