import unittest
from django.test import TestCase, RequestFactory, Client
from forklift.models import tracker_device
from deviceData.models import GPSData, EXTData
from forklift.views import deviceDashborad, tracker_device_list
from datetime import datetime, date, time
from django.urls import reverse
from django.http import JsonResponse, HttpRequest
from django.core import serializers
from django.utils import timezone
from django.contrib.auth.models import User
import json

class TestDeviceDashboard(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_device_dashboard(self):
        device = tracker_device.objects.create(device_id='sample_device_id')

        gps_data = GPSData.objects.create(
            device_id=device,
            state=1,
            latitude=0.0,
            longitude=0.0,
            time=datetime.now().time(),
            date=date.today(),
        )
        ext_data = EXTData.objects.create(device_id=device, date=date.today(), time=datetime.now().time(), batt_capacity=100)

    def test_device_dashboard_url(self):
        url = reverse('device_dashboard')
        self.assertEqual(url, '/devicedashboard')

class UpdateGPSTableViewTestCase(TestCase):
    def setUp(self):
        self.device = tracker_device.objects.create(device_id='TestDevice')

    def test_update_gps_table_view(self):      
        gps_data = GPSData.objects.create(
            device_id=self.device, 
            latitude=1.0, 
            longitude=1.0, 
            date=timezone.now().date(),
            time=timezone.now().time(),
            state=1         
        )

        self.assertIsNotNone(gps_data)

    def test_update_gpstable_url(self):
        url = reverse('update_gpstable')
        self.assertEqual(url, '/updategpstable')

class UpdateEXTTableViewTestCase(TestCase):
    def setUp(self):
        self.device = tracker_device.objects.create(device_id='TestDevice')

    def test_update_ext_table_view(self):
        ext_data = EXTData.objects.create(
            device_id=self.device,
            date=timezone.now().date(),
            time=timezone.now().time(),
            speed=10.0,
            batt_capacity=100
        )

        self.assertIsNotNone(ext_data)

    def test_update_exttable_url(self):
        url = reverse('update_exttable')
        self.assertEqual(url, '/updateexttable')
    
class ReportPageViewTestCase(TestCase):
    def test_report_page_view(self):
        client = Client()
        device_id = 'test_device_id'
        response = client.get(reverse('report_page'), {'deviceID': device_id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reportpage.html')

    def test_report_page_url(self):
        url = reverse('report_page')
        self.assertEqual(url, '/reportpage/')

class ListPageViewTestCase(TestCase):
    def test_list_page_view_authenticated(self):
        user = User.objects.create_user(username='testuser', password='password')
        client = Client()
        client.login(username='testuser', password='password')

        response = client.get(reverse('list_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listpage.html')

    def test_register_device_url(self):
        url = reverse('register_device')
        self.assertEqual(url, '/register/')

class RegisterDeviceTestCase(TestCase):
    def test_register_device_post_request_valid_form(self):
        data = {
            'device_id': 'TestDevice',
        }
        response = self.client.post(reverse('register_device'), data)
        self.assertEqual(response.status_code, 200)

    def test_list_page_url(self):
        url = reverse('list_page')
        self.assertEqual(url, '/listpage/')

class TrackerDeviceListViewTestCase(TestCase):
    def setUp(self):
        self.device1 = tracker_device.objects.create(
            device_id='TestDevice1',
            vehicle_name='Vehicle 1',
            device_model='Model 1',
            vehicle_id='Vehicle ID 1',
            driver='Driver 1',
            manufacturer='Manufacturer 1',
            hardware_version='Version 1.0',
            software_version='Software 1.0',
        )
        self.device2 = tracker_device.objects.create(
            device_id='TestDevice2',
            vehicle_name='Vehicle 2',
            device_model='Model 2',
            vehicle_id='Vehicle ID 2',
            driver='Driver 2',
            manufacturer='Manufacturer 2',
            hardware_version='Version 2.0',
            software_version='Software 2.0',
        )

    def test_tracker_device_list_view(self):
        factory = RequestFactory()
        request = factory.get(reverse('tracker-device-list'))
        response = tracker_device_list(request)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        data = json.loads(content)
        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]['device_id'], self.device1.device_id)
        self.assertEqual(data[0]['vehicle_name'], self.device1.vehicle_name)
        self.assertEqual(data[0]['device_model'], self.device1.device_model)

        self.assertEqual(data[1]['device_id'], self.device2.device_id)
        self.assertEqual(data[1]['vehicle_name'], self.device2.vehicle_name)
        self.assertEqual(data[1]['device_model'], self.device2.device_model)

    def test_tracker_device_url(self):
        url = reverse('tracker-device-list')
        self.assertEqual(url, '/listpage/api/tracker-devices/')

if __name__ == '__main__':
    unittest.main()
