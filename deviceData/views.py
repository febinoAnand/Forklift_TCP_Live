from django.http import JsonResponse
from rest_framework import serializers
from .models import EXTData, GPSData
from .serializers import EXTDataSerializer, GPSDataSerializer
from .import views
from datetime import datetime, date ,time
from django.db.models import Count


def ext_data_list(request):
    if request.method == 'GET':
        ext_data = EXTData.objects.all()
        serializer = EXTDataSerializer(ext_data, many=True)
        return JsonResponse(serializer.data, safe=False)

def gps_data_list(request):
    if request.method == 'GET':
        gps_data = GPSData.objects.all()
        serializer = GPSDataSerializer(gps_data, many=True)
        return JsonResponse(serializer.data, safe=False)
    
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