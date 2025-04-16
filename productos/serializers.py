from rest_framework import serializers
from .models import Producto

class HabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'
