from django.shortcuts import render, redirect
from django.http import JsonResponse
from forklift.models import tracker_device
from django.http import HttpResponse
from deviceData.models import GPSData,EXTData
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import TrackerDeviceSerializer
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import TrackerDeviceForm
from django.contrib.auth import authenticate, login
from django.core import serializers
import random
from datetime import datetime, date ,time ,timedelta


def loginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('listpage/')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})
    else:
        return render(request, 'login.html')

@login_required
def deviceDashborad(request):
    try:
        current_device_id = request.GET.get('device_id')
        # print (current_device_id)
        currentDevice = tracker_device.objects.get(device_id = current_device_id)
        gpsData = GPSData.objects.all()

        today = date.today() 
        start_time = datetime.combine(today, time.min)
        end_time = datetime.now()
        if len(gpsData) > 0:
            gpsData = gpsData.order_by('-pk')[0]

            data2 = GPSData.objects.filter(date=today, time__range=(start_time.time(), end_time.time())).order_by("time").values()
    
            lastTime = datetime.strptime("00:00:00", "%H:%M:%S")
            states = ["Inactive", "Idle", "Active", "Alert"]
            currentState = 1
            stateHr = [0,0,0,0]
            stateTiming = []
            
            for gpsData in data2:
                onOffStateDic = {}
                currentTime = datetime.strptime(str(gpsData["time"]), "%H:%M:%S")
                differencesInSeconds = (currentTime - lastTime).total_seconds()
                # print(currentTime , " - ", lastTime , " = ", differencesInSeconds , " - ", states[currentState-1], " - ", currentState)
                # stateHr[currentState-1] = stateHr[currentState-1] + differencesInSeconds
                
                onOffStateDic['state'] = states[currentState-1]
                onOffStateDic['timediff'] = differencesInSeconds
                onOffStateDic['percent'] = round(((differencesInSeconds / (60 * 60 * 24)) * 100),3)
                stateTiming.append(onOffStateDic)
                
                currentState = gpsData["state"]
                lastTime = currentTime
        else:
            gpsData = GPSData()
        extData = EXTData.objects.all()
        if len(extData) > 0:
            extData = extData.order_by('-pk')[0]
        else:
            extData = EXTData()
        
        # print (stateTiming)
        rand = random.randint(1,10)
        return render(request,"devicedashboard.html", {"device":currentDevice,"gpsData":gpsData,"random":rand,"extData":extData,"stateTiming":stateTiming})
    except Exception as e:
        print (e)
        return HttpResponse('Device Not found')
    

@login_required
def updateGPSTableView(request):
    currentDeviceID = request.GET['deviceID']
    if currentDeviceID != None:
        current_tracker_device = tracker_device.objects.get(device_id = currentDeviceID)
        gps_table_list = GPSData.objects.filter(device_id = current_tracker_device).filter(latitude__gt = 0.0).order_by('-pk')[:10]
        gps_table_json = serializers.serialize('json', gps_table_list)
        # print (gps_table_json)
    return HttpResponse(gps_table_json,content_type='application/json')

@login_required
def updateEXTTableView(request):
    currentDeviceID = request.GET['deviceID']
    if currentDeviceID != None:
        current_tracker_device = tracker_device.objects.get(device_id = currentDeviceID)
        ext_table_list = EXTData.objects.filter(device_id = current_tracker_device).order_by('-pk')[:10]
        ext_table_json = serializers.serialize('json', ext_table_list)
        # print (ext_table_json)
    return HttpResponse(ext_table_json,content_type='application/json')

@login_required
def report_page_view(request):
    currentDeviceID = request.GET.get('deviceID')
    return render(request, 'reportpage.html')

@login_required
def registration_view(request):
    if request.method == 'POST':
        return redirect('login')
    else:
        return render(request, 'registration.html')

@login_required
def list_page_view(request):
    return render(request, 'listpage.html')

@login_required
def register_device(request):
    if request.method == 'POST':
        form = TrackerDeviceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listpage.html') 
    else:
        form = TrackerDeviceForm()
    return render(request, 'registration.html', {'form': form})

@login_required    
def tracker_device_list(request):
    devices = tracker_device.objects.all()
    data = [{'device_id': device.device_id, 'vehicle_name': device.vehicle_name, 'device_model': device.device_model,
             'vehicle_id': device.vehicle_id, 'driver': device.driver, 'add_date': device.add_date.strftime('%Y-%m-%d'),
             'manufacturer': device.manufacturer, 'hardware_version': device.hardware_version,
             'software_version': device.software_version} for device in devices]
    return JsonResponse(data, safe=False)