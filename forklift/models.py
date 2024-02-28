from django.db import models

class tracker_device(models.Model):
    device_id = models.CharField(max_length = 15, unique=True, blank=False)
    vehicle_name = models.CharField(max_length = 20, blank=True)
    device_model = models.CharField(max_length = 20, blank=False)
    vehicle_id = models.CharField(max_length = 20, blank=False)
    driver = models.CharField(max_length = 20, blank=True)
    add_date = models.DateTimeField(auto_now_add=True)
    manufacturer = models.CharField(max_length = 20, blank=True)
    hardware_version = models.CharField(max_length = 10, blank=True)
    software_version = models.CharField(max_length = 10, blank=True)
   

    def __str__(self):
        return self.device_id
