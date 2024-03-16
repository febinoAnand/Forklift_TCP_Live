from rest_framework import serializers
from .models import EXTData, GPSData

class EXTDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EXTData
        fields = '__all__'

class GPSDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPSData
        fields = '__all__'
