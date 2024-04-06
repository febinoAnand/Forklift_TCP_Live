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
from django.contrib.auth import logout
from django.core import serializers
import random
from datetime import datetime, date ,time ,timedelta
from django.core.exceptions import ObjectDoesNotExist



def loginView(request):
    print("login....")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username)
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('listpage/')  
            else:
                login(request, user)
                return redirect('listpage/') 
        else:
            return render(request, 'login.html', {'error': True})
    else:
        print("get")
        return render(request, 'login.html')

def logoutView(request):
    logout(request)
    return redirect('/login')

def deviceDashborad(request):
    try:
        
        current_device_id = request.GET.get('device_id')
        print (current_device_id)
        currentDevice = tracker_device.objects.get(device_id = current_device_id)
        gps_data = GPSData.objects.filter(device_id=currentDevice)
        stateTiming = []
        today = date.today() 
        start_time = datetime.combine(today, time.min)
        end_time = datetime.now()
        if len(gps_data) > 0:
            gps_data = gps_data.order_by('-pk')[0]

            data2 = GPSData.objects.filter(device_id = currentDevice, date=today, time__range=(start_time.time(), end_time.time())).order_by("time").values()
    
            lastTime = datetime.strptime("00:00:00", "%H:%M:%S")
            states = ["Inactive", "Idle", "Active", "Alert"]
            currentState = 1
            stateHr = [0,0,0,0]
            
            
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
            gps_data = GPSData()
        ext_data = EXTData.objects.filter(device_id=currentDevice)
        if len(ext_data) > 0:
            ext_data = ext_data.order_by('-pk')[0]
        else:
            ext_data = EXTData()
        
        # print (stateTiming)
        rand = random.randint(1,10)
        return render(request,"devicedashboard.html", {"device":currentDevice,"gpsData":gps_data,"random":rand,"extData":ext_data,"stateTiming":stateTiming})
    except Exception as e:
        print (e)
        return HttpResponse('Device Not found')
    

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
    currentDeviceID = request.GET['deviceID']
    return render(request, 'reportpage.html',{'deviceID': currentDeviceID})


def registration_view(request):
    if request.method == 'POST':
        return redirect('login')
    else:
        return render(request, 'registration.html')


def list_page_view(request):
    if request.user.is_authenticated:
        return render(request, 'listpage.html')
    else:
        return redirect('/')


def register_device(request):
    if request.method == 'POST':
        form = TrackerDeviceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listpage.html') 
    else:
        form = TrackerDeviceForm()
    return render(request, 'registration.html', {'form': form})
    
def tracker_device_list(request):
    devices = tracker_device.objects.all()
    data = [{'device_id': device.device_id, 'vehicle_name': device.vehicle_name, 'device_model': device.device_model,
             'vehicle_id': device.vehicle_id, 'driver': device.driver, 'add_date': device.add_date.strftime('%Y-%m-%d'),
             'manufacturer': device.manufacturer, 'hardware_version': device.hardware_version,
             'software_version': device.software_version} for device in devices]
    return JsonResponse(data, safe=False)

def historypage(request):
    currentDeviceID = request.GET['deviceID']
    return render(request, 'historypage.html',{'deviceID': currentDeviceID})

def get_gps_data_for_date(request):
    if request.method == 'GET':
        currentDeviceID = request.GET.get('deviceID')
        selected_date_str = request.GET.get('date')
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        deviceObject = tracker_device.objects.get(device_id=currentDeviceID)
        
        start_time = datetime.combine(selected_date, time.min)
        end_time = datetime.combine(selected_date, time.max)
        
        data2 = GPSData.objects.filter(device_id=deviceObject, date=selected_date, time__range=(start_time.time(), end_time.time())).order_by("time").values()
        
        last_gps_data = GPSData.objects.filter(device_id=deviceObject).order_by('-date', '-time')[:5]
        
        lastTime = datetime.strptime("00:00:00", "%H:%M:%S")
        states = ["Inactive", "Idle", "Active", "Alert"]
        currentState = 1
        stateHr = [0, 0, 0, 0]
        for gpsData in data2:
            currentTime = datetime.strptime(str(gpsData["time"]), "%H:%M:%S")
            differencesInSeconds = (currentTime - lastTime).total_seconds()
            stateHr[currentState-1] += differencesInSeconds
            currentState = gpsData["state"]
            lastTime = currentTime
        
        res = [round(x / 3600, 2) for x in stateHr]
        response_data = []

        for n, item in enumerate(states):
            response_data.append({
                'state': item,
                'duration': res[n]
            })

        return JsonResponse(response_data, safe=False)
    
def updateEXTTabledateView(request):
    currentDeviceID = request.GET.get('deviceID')
    selected_date = request.GET.get('date')

    if currentDeviceID is not None and selected_date is not None:
        current_tracker_device = tracker_device.objects.get(device_id = currentDeviceID)
        ext_table_list = EXTData.objects.filter(device_id=current_tracker_device, date=selected_date).order_by('-pk')[:10]
        ext_table_json = serializers.serialize('json', ext_table_list)
    else:
        ext_table_json = '{"error": "Please provide both deviceID and date parameters."}'

    return HttpResponse(ext_table_json, content_type='application/json')

def updateGPSTabledateView(request):
    currentDeviceID = request.GET['deviceID']
    selected_date = request.GET.get('date')

    if currentDeviceID is not None and selected_date is not None:
        current_tracker_device = tracker_device.objects.get(device_id = currentDeviceID)
        gps_table_list = GPSData.objects.filter(device_id=current_tracker_device, date=selected_date).order_by('-pk')[:10]
        gps_table_json = serializers.serialize('json', gps_table_list)
    else:
        gps_table_json = '{"error": "Please provide both deviceID and date parameters."}'

    return HttpResponse(gps_table_json, content_type='application/json')
