from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import GPSData, EXTData, tracker_device
from .serializers import GPSDataSerializer
import json

class GPSDataSerializerTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_gps_data(self):
        tracker_device_id = 1
        tracker_device.objects.create(device_id=tracker_device_id)

        data = {
            'device_id': tracker_device_id,
            'latitude': 123.456,
            'longitude': 78.910,
            'distance': 50.25,
            'speed': 60.5,
            'state': 2,
            'date': '2024-03-06',
            'time': '14:30:00',
            'ignition': True,
            'movementState': True,
            'gsmOperatorCode': 1234,
            'gsmSignal': 5,
            'gsmAreaCode': 5678,
            'odometer': 10000,
            'satellite': 8
        }

        response = self.client.post(reverse('gps-data-list'), json.dumps(data), content_type='application/json')
        print(response.content)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GPSData.objects.count(), 1)
        gps_data = GPSData.objects.get()
        self.assertEqual(gps_data.latitude, 123.456)

class EXTDataSerializerTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_ext_data(self):
        tracker_device_id = 1
        tracker_device.objects.create(device_id=tracker_device_id)

        data = {
            'device_id': tracker_device_id,
            'server_date': '2024-03-06',
            'server_time': '14:30:00',
            'date': '2024-03-06',
            'time': '14:30:00',
            'speed': 60.5,
            'distance': 50.25,
            'batt_voltage': 12.5,
            'batt_amp': 2.5,
            'batt_capacity': 100,
            'batt_power': 30.5,
            'watt_hr': 500.75 
        }

        response = self.client.post(reverse('ext-data-list'), json.dumps(data), content_type='application/json')
        print(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EXTData.objects.count(), 1)
        ext_data = EXTData.objects.get()
        self.assertEqual(ext_data.speed, 60.5)