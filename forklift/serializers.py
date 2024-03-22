from rest_framework import serializers
from .models import tracker_device

class TrackerDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = tracker_device
        fields = '__all__'