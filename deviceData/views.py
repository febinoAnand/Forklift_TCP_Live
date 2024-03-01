from django.http import JsonResponse
from rest_framework import serializers
from .models import EXTData, GPSData
from .serializers import EXTDataSerializer, GPSDataSerializer
from .import views
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

def get_gps_data(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    gps_data = GPSData.objects.filter(date__range=[start_date, end_date]).values('state').annotate(count=Count('state'))

    data = {
        'active': 0,
        'inactive': 0,
        'idle': 0
    }

    for entry in gps_data:
        if entry['state'] == 1:
            data['inactive'] = entry['count']
        elif entry['state'] == 2:
            data['idle'] = entry['count']
        elif entry['state'] == 3:
            data['active'] = entry['count']

    return JsonResponse(data)