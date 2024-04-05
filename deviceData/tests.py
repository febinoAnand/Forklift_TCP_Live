from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import GPSData, EXTData, tracker_device
from .serializers import GPSDataSerializer
from .views import get_gps_data, get_last_data, get_today_gps_data, get_utilization_hours, search_data, generate_pdf, generate_csv
from datetime import date, datetime, time, timedelta
from django.http import JsonResponse

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

    def test_gps_data_url(self):
        url = reverse('gps-data-list')
        self.assertEqual(url, '/gps-data/')

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

    def test_ext_data_url(self):
        url = reverse('ext-data-list')
        self.assertEqual(url, '/ext-data/')

class GPSDataTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.device = tracker_device.objects.create(device_id="test_device")
        self.gps_data = GPSData.objects.create(
            device_id=self.device,
            latitude=1.23,
            longitude=4.56,
            distance=10,
            speed=20,
            state=3,
            date="2024-04-04",
            time="12:00:00",
            ignition=True,
            movementState=True,
            gsmOperatorCode=1234,
            gsmSignal=80,
            gsmAreaCode=5678,
            odometer=100,
            satellite=5
        )

    def test_get_gps_data(self):
        request = self.factory.get(reverse('get_gps_data'), {'deviceID': 'test_device'})
        response = get_gps_data(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['latitude'], 1.23)
        self.assertEqual(data[0]['longitude'], 4.56)

    def test_get_gps_data_url(self):
        url = reverse('get_gps_data')
        self.assertEqual(url, '/api/get-gps-data/')

class LastDataTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.device = tracker_device.objects.create(device_id="test_device")

        self.gps_data = [GPSData.objects.create(
            device_id=self.device,
            latitude=1.23,
            longitude=4.56,
            distance=10,
            speed=20,
            state=3,
            date="2024-04-04",
            time="12:00:0{}".format(i),
            ignition=True,
            movementState=True,
            gsmOperatorCode=1234,
            gsmSignal=80,
            gsmAreaCode=5678,
            odometer=100,
            satellite=5
        ) for i in range(5)]

        self.ext_data = [
            EXTData.objects.create(
                device_id=self.device,
                server_date="2024-04-04",
                server_time="12:00:0{}".format(i),
                date="2024-04-04",
                time="12:00:0{}".format(i),
                speed=20.5,
                distance=100.5,
                batt_voltage=12.3, 
                batt_amp=5.6,
                batt_capacity=100, 
                batt_power=60.2,
                watt_hr=200.5,
            ) for i in range(5)
        ]

    def test_get_last_data(self):
        request = self.factory.get(reverse('get_last_data'), {'deviceID': 'test_device'})
        response = get_last_data(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['gps_data']), 5)
        self.assertEqual(len(data['ext_data']), 5)

    def test_get_last_data_url(self):
        url = reverse('get_last_data')
        self.assertEqual(url, '/api/get_last_data/')

class GetTodayGPSDataTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.device = tracker_device.objects.create(device_id="test_device")
        today = date.today()
        GPSData.objects.create(
            device_id=self.device,
            latitude=1.23,
            longitude=4.56,
            distance=10,
            speed=20,
            state=1,
            date=today,
            time=datetime.strptime("08:00:00", "%H:%M:%S").time(),
            ignition=True,
            movementState=True,
            gsmOperatorCode=1234,
            gsmSignal=80,
            gsmAreaCode=5678,
            odometer=100,
            satellite=5
        )

    def test_get_today_gps_data(self):
        url = reverse('get_today_gps_data')
        request = self.factory.get(url, {'deviceID': 'test_device'})
        response = get_today_gps_data(request)

        self.assertEqual(response.status_code, 200)
        response_data = response.content.decode('utf-8')
        response_data = eval(response_data)
        self.assertEqual(len(response_data), 4)
        self.assertTrue(any(item['state'] == 'Inactive' for item in response_data))
        self.assertTrue(any(item['state'] == 'Idle' for item in response_data))
        self.assertTrue(any(item['state'] == 'Active' for item in response_data))
        self.assertTrue(any(item['state'] == 'Alert' for item in response_data))
        for item in response_data:
            self.assertTrue(item['duration'] >= 0)
        
    def test_get_today_gps_url(self):
        url = reverse('get_today_gps_data')
        self.assertEqual(url, '/get_today_gps_data/')

class GetUtilizationHoursTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.device = tracker_device.objects.create(device_id="test_device")
        today = date.today()
        GPSData.objects.create(
            device_id=self.device,
            latitude=1.23,
            longitude=4.56,
            distance=10,
            speed=20,
            state=1,
            date=today - timedelta(days=7),
            time=datetime.strptime("08:00:00", "%H:%M:%S").time(),
            ignition=True,
            movementState=True,
            gsmOperatorCode=1234,
            gsmSignal=80,
            gsmAreaCode=5678,
            odometer=100,
            satellite=5
        )

    def test_get_utilization_hours(self):
        url = reverse('get_utilization_hours')
        request = self.factory.get(url, {'deviceID': 'test_device'})
        response = get_utilization_hours(request)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(isinstance(response_data, dict))
        self.assertEqual(len(response_data), 7)
        for day, data in response_data.items():
            self.assertTrue("Inactive" in data)
            self.assertTrue("Idle" in data)
            self.assertTrue("Active" in data)
            self.assertTrue("Total" in data)
            self.assertTrue(isinstance(data["Inactive"], float))
            self.assertTrue(isinstance(data["Idle"], float))
            self.assertTrue(isinstance(data["Active"], float))
            self.assertTrue(isinstance(data["Total"], float))

    def test_get_utilization_hours_url(self):
        url = reverse('get_utilization_hours')
        self.assertEqual(url, '/get_utilization_hours/')

class SearchDataViewTestCase(TestCase):
    def setUp(self):
        self.device_id = 'test_device'
        tracker_device.objects.create(device_id=self.device_id)

    def test_search_data_view(self):
        factory = RequestFactory()
        request = factory.get('/search_data/', {
            'deviceID': self.device_id,
            'fromDate': '2024-01-01',
            'toDate': '2024-01-07'
        })
        response = search_data(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)

    def test_search_data_url(self):
        url = reverse('search_data')
        self.assertEqual(url, '/search_data/')

class GeneratePDFViewTestCase(TestCase):
    def setUp(self):
        self.device_id = 'test_device'
        tracker_device.objects.create(device_id=self.device_id)

    def test_generate_pdf(self):
        factory = RequestFactory()
        request = factory.get('/generate-pdf/', {
            'deviceID': self.device_id,
            'fromDate': '2024-01-01',
            'toDate': '2024-01-07'
        })
        response = generate_pdf(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.has_header('Content-Disposition'))
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="Forklift.pdf"'
        )
        with open('generated_pdf.pdf', 'wb') as f:
            f.write(response.content)
        self.assertTrue(len(response.content) > 0)

    def test_generate_pdf_url(self):
        url = reverse('generate_pdf')
        self.assertEqual(url, '/generate-pdf/')

class GenerateCSVViewTestCase(TestCase):
    def setUp(self):
        self.device_id = 'test_device'
        tracker_device.objects.create(device_id=self.device_id)

    def test_generate_csv(self):
        factory = RequestFactory()
        request = factory.get('/generate-csv/', {
            'deviceID': self.device_id,
            'fromDate': '2024-01-01',
            'toDate': '2024-01-07'
        })
        response = generate_csv(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertTrue(response.has_header('Content-Disposition'))
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="report.csv"'
        )
        with open('generated_report.csv', 'wb') as f:
            f.write(response.content)
        self.assertTrue(len(response.content) > 0)

    def test_generate_csv_url(self):
        url = reverse('generate_csv')
        self.assertEqual(url, '/generate-csv/')