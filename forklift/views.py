from django.shortcuts import render, redirect
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

def registration_view(request):
    if request.method == 'POST':
        return redirect('login')
    else:
        return render(request, 'registration.html')

def list_page_view(request):
    return render(request, 'listpage.html')

def register(request):
    if request.method == 'POST':

        device_id = request.POST.get('deviceId')
        vehicle_name = request.POST.get('vehicleName')
        device_model = request.POST.get('deviceModel')
        vehicle_id = request.POST.get('vehicleId')
        driver = request.POST.get('driver')
        manufacturer = request.POST.get('manufacturer')
        hardware_version = request.POST.get('hardwareVersion')
        software_version = request.POST.get('softwareVersion')

        new_device = tracker_device.objects.create(
            device_id=device_id,
            vehicle_name=vehicle_name,
            device_model=device_model,
            vehicle_id=vehicle_id,
            driver=driver,
            manufacturer=manufacturer,
            hardware_version=hardware_version,
            software_version=software_version
        )
        new_device.save()
        return redirect('login')
    else:
        return render(request, 'registration.html')