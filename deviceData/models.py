from django.db import models
from forklift.models import tracker_device

# Create your models here.


class RAWData(models.Model):
    device_id = models.CharField(max_length = 15, blank=False)
    received_time = models.DateTimeField(blank=False)
    data_length = models.IntegerField(blank=False)
    data = models.CharField(max_length=4096,blank=False)

    def __str__(self):
        return self.device_id

class GPSData(models.Model):
    state_choice = [ (1,"Inactive"), (2,"Idle"), (3,"Active")]    # 1-Inactive  2-Idle  3-Active
    device_id = models.ForeignKey(tracker_device, on_delete=models.CASCADE, related_name= "imei_id")
    latitude = models.FloatField()
    longitude = models.FloatField()
    distance = models.DecimalField(default=0,decimal_places = 2, max_digits = 10)
    speed = models.DecimalField(default=0,decimal_places = 2, max_digits = 5)
    state = models.IntegerField(choices = state_choice)
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return ( str(self.date) +"_"+ str(self.time) + " // " + self.device_id.device_id)



class EXTData(models.Model):
    device_id = models.ForeignKey(tracker_device, on_delete=models.CASCADE)
    server_date = models.DateField(auto_now_add = True)
    server_time = models.TimeField(auto_now_add = True)
    date = models.DateField()
    time = models.TimeField()
    speed = models.DecimalField(default=0,decimal_places = 2, max_digits = 5)
    distance = models.DecimalField(default=0,decimal_places = 2, max_digits = 10)
    batt_voltage = models.DecimalField(default=0,decimal_places = 2, max_digits = 5)
    batt_amp = models.DecimalField(default=0,decimal_places = 2, max_digits = 5)
    batt_capacity = models.IntegerField()
    batt_power = models.DecimalField(default=0,decimal_places = 2, max_digits = 8)
    watt_hr = models.DecimalField(default=0,decimal_places = 2, max_digits = 10)

