from django.http import JsonResponse
from rest_framework import serializers
from .models import EXTData, GPSData
from .serializers import EXTDataSerializer, GPSDataSerializer
from .import views
from datetime import datetime, date ,time ,timedelta
from django.db.models import Count
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
import json


def ext_data_list(request):
    if request.method == 'GET':
        ext_data = EXTData.objects.all()
        serializer = EXTDataSerializer(ext_data, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        serializer = EXTDataSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

def gps_data_list(request):
    if request.method == 'GET':
        gps_data = GPSData.objects.all()
        serializer = GPSDataSerializer(gps_data, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = GPSDataSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def get_gps_data(request):
    gps_data = GPSData.objects.all().values('latitude', 'longitude') 
    return JsonResponse(list(gps_data), safe=False)
    
def get_last_data(request):
    last_gps_data = GPSData.objects.order_by('-date', '-time')[:5]
    last_ext_data = EXTData.objects.order_by('-date', '-time')[:5]

    gps_serializer = GPSDataSerializer(last_gps_data, many=True)
    ext_serializer = EXTDataSerializer(last_ext_data, many=True)

    return JsonResponse({'gps_data': gps_serializer.data, 'ext_data': ext_serializer.data})

def get_today_gps_data(request):
    today = date.today()
    start_time = datetime.combine(today, time.min)
    end_time = datetime.now()

    data = GPSData.objects.filter(date=today, time__range=(start_time.time(), end_time.time())) \
        .values('state') \
        .annotate(count=Count('state'))

    active = 0
    inactive = 0
    idle = 0

    for item in data:
        if item['state'] == 1:
            inactive = item['count']
        elif item['state'] == 2:
            idle = item['count']
        elif item['state'] == 3:
            active = item['count']

    return JsonResponse({'active': active, 'idle': idle, 'inactive': inactive})

def get_utilization_hours(request):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)

    gps_data = GPSData.objects.filter(date__range=[start_date, end_date])

    utilization_hours = {}
    for day in range(6):
        current_date = start_date + timedelta(days=day)
        day_data = gps_data.filter(date=current_date)
        total_utilization_hours = sum([data.distance for data in day_data])
        utilization_hours[current_date.strftime('%A')] = total_utilization_hours

    return JsonResponse(utilization_hours)

def search_data(request):
    from_date = request.GET.get('fromDate')
    to_date = request.GET.get('toDate')

    filtered_data = EXTData.objects.filter(
        date__range=[from_date, to_date]
    ).values('date', 'time', 'distance', 'speed', 'watt_hr', 'batt_voltage', 'batt_amp', 'batt_power', 'batt_capacity')

    return JsonResponse(list(filtered_data), safe=False)