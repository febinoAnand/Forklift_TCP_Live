from django.contrib import admin
from .models import tracker_device
# Register your models here.

class trackerDeviceAdmin(admin.ModelAdmin):
    list_display = ["device_id","vehicle_name","device_model","vehicle_id","driver"]
    

admin.site.register(tracker_device,trackerDeviceAdmin)


