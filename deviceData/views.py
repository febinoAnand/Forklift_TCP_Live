from django.http import JsonResponse
from rest_framework import serializers
from .models import EXTData, GPSData
from .serializers import EXTDataSerializer, GPSDataSerializer
from .import views


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