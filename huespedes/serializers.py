from rest_framework import serializers
from .models import Huesped

class HuespedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Huesped
        fields = '__all__'
