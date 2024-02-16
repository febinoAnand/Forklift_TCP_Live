from django.contrib import admin
from .models import GPSData, RAWData, EXTData
# Register your models here.


class GPSDataAdmin(admin.ModelAdmin):
    list_display = ["date","time", "device_id","latitude", "longitude", "distance", "speed", "state"]

class RAWDataAdmin(admin.ModelAdmin):
    list_display = ["received_time", "device_id", "data_length", "data"]

class EXTDataAdmin(admin.ModelAdmin):
    list_display = ["date","time", "device_id", "device_id", "speed", "distance","batt_voltage","batt_amp","batt_capacity","batt_power","watt_hr"]


admin.site.register(EXTData, EXTDataAdmin)
admin.site.register(RAWData, RAWDataAdmin)
admin.site.register(GPSData, GPSDataAdmin)
