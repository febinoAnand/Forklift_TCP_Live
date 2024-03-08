from django.shortcuts import render
from forklift.models import tracker_device
from django.http import HttpResponse
from deviceData.models import GPSData,EXTData

from django.core import serializers
import random

def loginView(request):
    return render(request,'login.html')

def deviceDashborad(request):
    currentDevice = tracker_device.objects.get(device_id = '352592573198322')
    gpsData = GPSData.objects.all().order_by('-pk')[0]
    extData = EXTData.objects.all().order_by('-pk')[0]
    rand = random.randint(1,10)
    # print(gpsData)
    return render(request,"devicedashboard.html", {"device":currentDevice,"gpsData":gpsData,"random":rand,"extData":extData})


def updateGPSTableView(request):
    currentDeviceID = request.GET['deviceID']
    if currentDeviceID != None:
        current_tracker_device = tracker_device.objects.get(device_id = currentDeviceID)
        gps_table_list = GPSData.objects.filter(device_id = current_tracker_device).filter(latitude__gt = 0.0).order_by('-pk')[:10]
        gps_table_json = serializers.serialize('json', gps_table_list)
        # print (gps_table_json)
    return HttpResponse(gps_table_json,content_type='application/json')

def updateEXTTableView(request):
    currentDeviceID = request.GET['deviceID']
    if currentDeviceID != None:
        current_tracker_device = tracker_device.objects.get(device_id = currentDeviceID)
        ext_table_list = EXTData.objects.filter(device_id = current_tracker_device).order_by('-pk')[:10]
        ext_table_json = serializers.serialize('json', ext_table_list)
        # print (ext_table_json)
    return HttpResponse(ext_table_json,content_type='application/json')

def report_page_view(request):
    return render(request, 'reportpage.html')