from rest_framework import serializers
from .models import Consumos

class HabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumos
        fields = '__all__'
