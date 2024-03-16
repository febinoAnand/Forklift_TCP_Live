from django import forms
from .models import tracker_device

class TrackerDeviceForm(forms.ModelForm):
    class Meta:
        model = tracker_device
        fields = '__all__'