from re import S
from django.http import JsonResponse
from rest_framework import serializers
from .models import EXTData, GPSData
from .serializers import EXTDataSerializer, GPSDataSerializer
from .import views
from datetime import datetime ,time ,timedelta
from django.db.models import Count ,Sum , F, DecimalField
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
import json
import csv
from decimal import Decimal
from django.http import HttpResponse
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,  Paragraph, Spacer
from forklift.models import tracker_device
from django.views import View
from datetime import date

def ext_data_list(request):
   
    if request.method == 'GET':
        currentDeviceID = request.GET.get('deviceID')
        # currentDevice = currentDeviceID.objects.get(deviceID=currentDeviceID)
        # print ("ext--->", currentDeviceID)
        # if currentDeviceID:
        deviceObject = tracker_device.objects.get(device_id = currentDeviceID)
        ext_data = EXTData.objects.filter(device_id=deviceObject).order_by('-id')[:1]
        # else:
            # ext_data = [EXTData.objects.latest('deviceID')]
            
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
        currentDeviceID = request.GET.get('deviceID')
        # print ("gps--->", currentDeviceID)
        deviceObject = tracker_device.objects.get(device_id = currentDeviceID)
        gps_data = GPSData.objects.filter(device_id=deviceObject).order_by('-id')[:1]

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
    if request.method == 'GET':
        currentDeviceID = request.GET.get('deviceID')
        # print ("gps--->", currentDeviceID)
        deviceObject = tracker_device.objects.get(device_id=currentDeviceID)
        gps_data = GPSData.objects.filter(device_id=deviceObject).values('latitude', 'longitude')
        return JsonResponse(list(gps_data), safe=False)
    
def get_last_data(request):
    if request.method == 'GET':
        currentDeviceID = request.GET.get('deviceID')
        # print ("gps--->", currentDeviceID)
        deviceObject = tracker_device.objects.get(device_id=currentDeviceID)
        
        last_gps_data = GPSData.objects.filter(device_id=deviceObject).order_by('-date', '-time')[:5]
        last_ext_data = EXTData.objects.filter(device_id=deviceObject).order_by('-date', '-time')[:5]

        gps_serializer = GPSDataSerializer(last_gps_data, many=True)
        ext_serializer = EXTDataSerializer(last_ext_data, many=True)

        return JsonResponse({'gps_data': gps_serializer.data, 'ext_data': ext_serializer.data})

def get_today_gps_data(request):
    if request.method == 'GET':
        currentDeviceID = request.GET.get('deviceID')
        # print ("gps--->", currentDeviceID)
        deviceObject = tracker_device.objects.get(device_id=currentDeviceID)
        today = date.today() 
        start_time = datetime.combine(today, time.min)
        end_time = datetime.now()
    # end_time = datetime.strptime("2023-03-23 23:59:59", "%Y-%m-%d %H:%M:%S")

    # print (start_time,"-", end_time)

    # data = GPSData.objects.filter(date=today, time__range=(start_time.time(), end_time.time())) \
    #                       .values('state') \
    #                       .annotate(duration=Count('state'))
    
    data2 = GPSData.objects.filter(device_id=deviceObject, date=today, time__range=(start_time.time(), end_time.time())).order_by("time").values()
        
    last_gps_data = GPSData.objects.filter(device_id=deviceObject).order_by('-date', '-time')[:5]
    
    lastTime = datetime.strptime("00:00:00", "%H:%M:%S")
    states = ["Inactive", "Idle", "Active", "Alert"]
    currentState = 1
    stateHr = [0,0,0,0]
    for gpsData in data2:
        currentTime = datetime.strptime(str(gpsData["time"]), "%H:%M:%S")
        differencesInSeconds = (currentTime - lastTime).total_seconds()
        # print(currentTime , " - ", lastTime , " = ", differencesInSeconds , " - ", states[currentState-1], " - ", currentState)
        stateHr[currentState-1] = stateHr[currentState-1] + differencesInSeconds
        
        currentState = gpsData["state"]
        lastTime = currentTime
    res = [round(x/3600,2) for x in stateHr]
    response_data = []

    for n,item in enumerate(states):
        response_data.append({
            'state': item,
            'duration': res[n]
        })

    return JsonResponse(response_data, safe=False)

def get_utilization_hours(request):
    currentDeviceID = request.GET.get('deviceID')
    try:
        deviceObject = tracker_device.objects.get(device_id=currentDeviceID)
    except tracker_device.DoesNotExist:
        return JsonResponse({"error": "Device not found"}, status=404)

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    utilization_hours = {}

    for day in range(7):
        current_date = start_date + timedelta(days=day)
        
        gps_data = GPSData.objects.filter(device_id=deviceObject, date=current_date).order_by('time')

        state_hours = [0, 0, 0]

        last_time = datetime.combine(current_date, datetime.min.time())
        for state in range(1, 4):
            state_data = gps_data.filter(state=state)
            for data_point in state_data:
                current_time = datetime.combine(current_date, data_point.time)
                difference_seconds = (current_time - last_time).total_seconds()
                if difference_seconds > 0:  
                    state_hours[state - 1] += difference_seconds
                last_time = current_time

        total_state_hours = sum(state_hours)
        if total_state_hours > 86400:  
            state_hours = [hour * 86400 / total_state_hours for hour in state_hours]
        total_utilization = sum(state_hours) / 3600
        utilization_hours[current_date.strftime('%A')] = {
            "Inactive": state_hours[0] / 3600,  
            "Idle": state_hours[1] / 3600,
            "Active": state_hours[2] / 3600,
            'Total':total_utilization 
        }
 
    return JsonResponse(utilization_hours)

def get_utilization_hours_for_report(deviceId, fromdate, todate):
    try:
        deviceObject = tracker_device.objects.get(device_id=deviceId)
    except tracker_device.DoesNotExist:
        return {"error": "Device not found"}

    utilization_hours = {}

    for day in range((todate - fromdate).days + 1):
        current_date = fromdate + timedelta(days=day)
        gps_data = GPSData.objects.filter(device_id=deviceObject, date=current_date).order_by('time')

        state_hours = [0, 0, 0]

        last_time = datetime.combine(current_date, datetime.min.time())
        for state in range(1, 4):
            state_data = gps_data.filter(state=state)
            for data_point in state_data:
                current_time = datetime.combine(current_date, data_point.time)
                difference_seconds = (current_time - last_time).total_seconds()
                if difference_seconds > 0:
                    state_hours[state - 1] += difference_seconds
                last_time = current_time

        total_state_hours = sum(state_hours)
        if total_state_hours > 86400:
            state_hours = [hour * 86400 / total_state_hours for hour in state_hours]
        total_utilization = sum(state_hours) / 3600
        utilization_hours[current_date.strftime('%A')] = {
            "Inactive": state_hours[0] / 3600,
            "Idle": state_hours[1] / 3600,
            "Active": state_hours[2] / 3600,
            'Total': total_utilization
        }

    return utilization_hours

def search_data(request):
    if request.method == 'GET':
        currentDeviceID = request.GET.get('deviceID')
        from_date = datetime.strptime(request.GET.get('fromDate'), '%Y-%m-%d').date()
        to_date = datetime.strptime(request.GET.get('toDate'), '%Y-%m-%d').date()

        utilization_hours = get_utilization_hours_for_report(currentDeviceID, from_date, to_date)

        deviceObject = tracker_device.objects.get(device_id=currentDeviceID)
        gps_data = GPSData.objects.filter(device_id=deviceObject, date__range=[from_date, to_date])
        ext_data = EXTData.objects.filter(device_id=deviceObject, date__range=[from_date, to_date])

        data = []

        for date in set(gps_data.values_list('date', flat=True)) | set(ext_data.values_list('date', flat=True)):
            gps_distance = gps_data.filter(date=date).aggregate(Sum('distance'))['distance__sum'] or 0
            ext_distance = ext_data.filter(date=date).aggregate(Sum('distance'))['distance__sum'] or 0
            watt_hr = ext_data.filter(date=date).aggregate(Sum('watt_hr'))['watt_hr__sum'] or 0

            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'gps_distance': gps_distance,
                'ext_distance': ext_distance,
                'watt_hr': watt_hr,
                'utilization_hours': utilization_hours.get(date.strftime('%A'), {})
            })

        return JsonResponse(data, safe=False)

def generate_pdf(request):
    currentDeviceID = request.GET.get('deviceID')
    deviceObject = tracker_device.objects.get(device_id=currentDeviceID)
    from_date = datetime.strptime(request.GET.get('fromDate'), '%Y-%m-%d').date()
    to_date = datetime.strptime(request.GET.get('toDate'), '%Y-%m-%d').date()
    utilization_hours = get_utilization_hours_for_report(currentDeviceID, from_date, to_date)
    gps_data = GPSData.objects.filter(device_id=deviceObject, date__range=[from_date, to_date])
    ext_data = EXTData.objects.filter(device_id=deviceObject, date__range=[from_date, to_date])
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Forklift.pdf"'
    pdf = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    center_style = ParagraphStyle(name='Center', parent=styles['Normal'], alignment=1)
    content = []
    title = Paragraph("<b>INNOSPACE</b><br/><br/>", center_style)
    content.append(title)
    content.append(Spacer(1, 0.2 * inch))
    phone_email = Paragraph("<b>Phone:</b> +91-44-45550419<br/><b>Email:</b> info@innospace.co.in", styles['Normal'])
    content.append(phone_email)
    content.append(Spacer(1, 0.5 * inch))
    table_data = [['Date', 'GPS Distance', 'ODOMETER Distance', 'Watt HR', 'Utilization Hours']]

    for date in set(gps_data.values_list('date', flat=True)) | set(ext_data.values_list('date', flat=True)):
        gps_distance = gps_data.filter(date=date).aggregate(Sum('distance'))['distance__sum'] or 0
        ext_distance = ext_data.filter(date=date).aggregate(Sum('distance'))['distance__sum'] or 0
        watt_hr = ext_data.filter(date=date).aggregate(Sum('watt_hr'))['watt_hr__sum'] or 0

        active_hours = utilization_hours.get(date.strftime('%A'), {}).get('Active', 0)
        inactive_hours = utilization_hours.get(date.strftime('%A'), {}).get('Inactive', 0)
        idle_hours = utilization_hours.get(date.strftime('%A'), {}).get('Idle', 0)

        table_data.append([
            date.strftime('%Y-%m-%d'),
            gps_distance,
            ext_distance,
            watt_hr,
            f"Active: {active_hours:.2f} Inactive: {inactive_hours:.2f} Idle: {idle_hours:.2f}"
        ])
    table = Table(table_data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    content.append(table)
    pdf.build(content)

    return response


def generate_csv(request):
    device_id = request.GET.get('deviceID')
    from_date = request.GET.get('fromDate')
    to_date = request.GET.get('toDate')

    try:
        device_object = tracker_device.objects.get(device_id=device_id)
    except tracker_device.DoesNotExist:
        return HttpResponse("Device not found", status=404)
    from_date = datetime.strptime(from_date, "%Y-%m-%d")
    to_date = datetime.strptime(to_date, "%Y-%m-%d")
    utilization_hours = get_utilization_hours_for_report(device_id, from_date, to_date)
    gps_data = GPSData.objects.filter(device_id=device_object, date__range=[from_date, to_date])
    ext_data = EXTData.objects.filter(device_id=device_object, date__range=[from_date, to_date])
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'GPS Distance', 'ODOMETER Distance', 'Watt HR', 'Active Hours', 'Inactive Hours', 'Idle Hours'])

    for date in set(gps_data.values_list('date', flat=True)) | set(ext_data.values_list('date', flat=True)):
        formatted_date = date.strftime('%Y-%m-%d') 

    for date in set(gps_data.values_list('date', flat=True)) | set(ext_data.values_list('date', flat=True)):
        gps_distance = gps_data.filter(date=date).aggregate(Sum('distance'))['distance__sum'] or 0
        ext_distance = ext_data.filter(date=date).aggregate(Sum('distance'))['distance__sum'] or 0
        watt_hr = ext_data.filter(date=date).aggregate(Sum('watt_hr'))['watt_hr__sum'] or 0

        active_hours = utilization_hours.get(date.strftime('%A'), {}).get('Active', 0)
        inactive_hours = utilization_hours.get(date.strftime('%A'), {}).get('Inactive', 0)
        idle_hours = utilization_hours.get(date.strftime('%A'), {}).get('Idle', 0)

        writer.writerow([date, gps_distance, ext_distance, watt_hr, active_hours, inactive_hours, idle_hours])

    return response

def get_gps_date_data(request):
    if request.method == 'GET':
        currentDeviceID = request.GET.get('deviceID')
        selectedDate = request.GET.get('date')
        startTime = request.GET.get('startTime')
        endTime = request.GET.get('endTime')

        if not selectedDate:
            return JsonResponse([], safe=False)
        
        selected_date = datetime.strptime(selectedDate, '%Y-%m-%d').date()

        try:
            deviceObject = tracker_device.objects.get(device_id=currentDeviceID)
            gps_data = GPSData.objects.filter(device_id=deviceObject, date=selected_date)
            
            if startTime and endTime:
                start_time = datetime.strptime(startTime, '%H:%M').time()
                end_time = datetime.strptime(endTime, '%H:%M').time()
                gps_data = gps_data.filter(time__range=(start_time, end_time))
                
            gps_data = gps_data.values('latitude', 'longitude')
            
            return JsonResponse(list(gps_data), safe=False)
        except tracker_device.DoesNotExist:
            return JsonResponse([], safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
def get_utilization_date_hours(request):
    currentDeviceID = request.GET.get('deviceID')
    selected_date = request.GET.get('date')
    start_time = request.GET.get('startTime')
    end_time = request.GET.get('endTime')

    try:
        deviceObject = tracker_device.objects.get(device_id=currentDeviceID)
    except tracker_device.DoesNotExist:
        return JsonResponse({"error": "Device not found"}, status=404)

    utilization_hours = {}

    try:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({"error": "Invalid date format"}, status=400)

    gps_data = GPSData.objects.filter(device_id=deviceObject, date=selected_date).order_by('time')

    if start_time:
        start_time = datetime.strptime(start_time, '%H:%M').time()
        gps_data = gps_data.filter(time__gte=start_time)

    if end_time:
        end_time = datetime.strptime(end_time, '%H:%M').time()
        gps_data = gps_data.filter(time__lte=end_time)

    state_hours = [0, 0, 0]

    last_time = datetime.combine(selected_date, datetime.min.time())
    for state in range(1, 4):
        state_data = gps_data.filter(state=state)
        for data_point in state_data:
            current_time = datetime.combine(selected_date, data_point.time)
            difference_seconds = (current_time - last_time).total_seconds()
            if difference_seconds > 0:  
                state_hours[state - 1] += difference_seconds
            last_time = current_time

    total_state_hours = sum(state_hours)
    if total_state_hours > 86400:  
        state_hours = [hour * 86400 / total_state_hours for hour in state_hours]
    total_utilization = sum(state_hours) / 3600
    utilization_hours[selected_date.strftime('%A')] = {
        "Inactive": state_hours[0] / 3600,  
        "Idle": state_hours[1] / 3600,
        "Active": state_hours[2] / 3600,
        'Total': total_utilization 
    }

    return JsonResponse(utilization_hours)

def ext_data_date_list(request):
    if request.method == 'GET':
        selected_date = request.GET.get('date')
        current_device_id = request.GET.get('deviceID')

        device_object = tracker_device.objects.get(device_id=current_device_id)
        ext_data = EXTData.objects.filter(device_id=device_object, date=selected_date).order_by('-id')

        serializer = EXTDataSerializer(ext_data, many=True)
        return JsonResponse(serializer.data, safe=False)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        serializer = EXTDataSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

def gps_data_date_list(request):
    if request.method == 'GET':
        current_device_id = request.GET.get('deviceID')
        selected_date = request.GET.get('date')

        device_object = tracker_device.objects.get(device_id=current_device_id)
        
        if selected_date:
            gps_data = GPSData.objects.filter(device_id=device_object, date=selected_date).order_by('-id')
        else:
            gps_data = GPSData.objects.filter(device_id=device_object).order_by('-id')[:1]

        serializer = GPSDataSerializer(gps_data, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = GPSDataSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def get_last_date_data(request):
    if request.method == 'GET':
        current_device_id = request.GET.get('deviceID')
        selected_date = request.GET.get('date')
        
        device_object = tracker_device.objects.get(device_id=current_device_id)
        
        gps_data_queryset = GPSData.objects.filter(device_id=device_object)
        ext_data_queryset = EXTData.objects.filter(device_id=device_object)

        if selected_date:
            try:
                selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
                gps_data_queryset = gps_data_queryset.filter(date=selected_date)
                ext_data_queryset = ext_data_queryset.filter(date=selected_date)
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=400)

        last_gps_data = gps_data_queryset.order_by('-date', '-time')[:5]
        last_ext_data = ext_data_queryset.order_by('-date', '-time')[:5]

        gps_serializer = GPSDataSerializer(last_gps_data, many=True)
        ext_serializer = EXTDataSerializer(last_ext_data, many=True)

        return JsonResponse({'gps_data': gps_serializer.data, 'ext_data': ext_serializer.data})
    
def get_today_gps_date_data(request):
    if request.method == 'GET':
        currentDeviceID = request.GET.get('deviceID')
        selectedDate = request.GET.get('date')
        startTime = request.GET.get('startTime')
        endTime = request.GET.get('endTime')

        deviceObject = tracker_device.objects.get(device_id=currentDeviceID)
        if selectedDate:
            selected_date = datetime.strptime(selectedDate, '%Y-%m-%d').date()
        else:
            selected_date = date.today()

        if startTime:
            start_time = datetime.combine(selected_date, datetime.strptime(startTime, '%H:%M').time())
        else:
            start_time = datetime.combine(selected_date, time.min)

        if endTime:
            end_time = datetime.combine(selected_date, datetime.strptime(endTime, '%H:%M').time())
        else:
            end_time = datetime.now()

        data2 = GPSData.objects.filter(device_id=deviceObject, date=selected_date, time__range=(start_time.time(), end_time.time())).order_by("time").values()

        last_gps_data = GPSData.objects.filter(device_id=deviceObject).order_by('-date', '-time')[:5]

        lastTime = datetime.strptime("00:00:00", "%H:%M:%S")
        states = ["Inactive", "Idle", "Active", "Alert"]
        currentState = 1
        stateHr = [0,0,0,0]
        for gpsData in data2:
            currentTime = datetime.strptime(str(gpsData["time"]), "%H:%M:%S")
            differencesInSeconds = (currentTime - lastTime).total_seconds()
            stateHr[currentState-1] = stateHr[currentState-1] + differencesInSeconds
            currentState = gpsData["state"]
            lastTime = currentTime

        res = [round(x/3600, 2) for x in stateHr]

        response_data = []
        for n, item in enumerate(states):
            response_data.append({
                'state': item,
                'duration': res[n]
            })

        return JsonResponse(response_data, safe=False)
    
class CombinedDataView(View):
    def get(self, request):
        if 'ext-data' in request.path:
            current_device_id = request.GET.get('deviceID')
            try:
                device_object = tracker_device.objects.get(device_id=current_device_id)
                ext_data = EXTData.objects.filter(device_id=device_object).order_by('-id')[:1]
                serializer = EXTDataSerializer(ext_data, many=True)
                return JsonResponse(serializer.data, safe=False)
            except tracker_device.DoesNotExist:
                return HttpResponse(status=404)

        elif 'gps-data' in request.path:
            current_device_id = request.GET.get('deviceID')
            try:
                device_object = tracker_device.objects.get(device_id=current_device_id)
                gps_data = GPSData.objects.filter(device_id=device_object).order_by('-id')[:1]
                serializer = GPSDataSerializer(gps_data, many=True)
                return JsonResponse(serializer.data, safe=False)
            except tracker_device.DoesNotExist:
                return HttpResponse(status=404)

        elif 'get_last_data' in request.path:
            current_device_id = request.GET.get('deviceID')
            try:
                device_object = tracker_device.objects.get(device_id=current_device_id)
                last_gps_data = GPSData.objects.filter(device_id=device_object).order_by('-date', '-time')[:5]
                last_ext_data = EXTData.objects.filter(device_id=device_object).order_by('-date', '-time')[:5]
                gps_serializer = GPSDataSerializer(last_gps_data, many=True)
                ext_serializer = EXTDataSerializer(last_ext_data, many=True)
                return JsonResponse({'gps_data': gps_serializer.data, 'ext_data': ext_serializer.data})
            except tracker_device.DoesNotExist:
                return HttpResponse(status=404)

        elif 'get_today_gps_data' in request.path:
            current_device_id = request.GET.get('deviceID')
            try:
                device_object = tracker_device.objects.get(device_id=current_device_id)
                today = datetime.today() 
                start_time = datetime.combine(today, time.min)
                end_time = datetime.now()

                data2 = GPSData.objects.filter(device_id=device_object, date=today, time__range=(start_time.time(), end_time.time())).order_by("time").values()

                lastTime = datetime.strptime("00:00:00", "%H:%M:%S")
                states = ["Inactive", "Idle", "Active", "Alert"]
                currentState = 1
                stateHr = [0,0,0,0]
                for gpsData in data2:
                    currentTime = datetime.strptime(str(gpsData["time"]), "%H:%M:%S")
                    differencesInSeconds = (currentTime - lastTime).total_seconds()
                    stateHr[currentState-1] = stateHr[currentState-1] + differencesInSeconds
                    currentState = gpsData["state"]
                    lastTime = currentTime
                res = [round(x/3600,2) for x in stateHr]
                response_data = []

                for n,item in enumerate(states):
                    response_data.append({
                        'state': item,
                        'duration': res[n]
                    })

                return JsonResponse(response_data, safe=False)

            except tracker_device.DoesNotExist:
                return HttpResponse(status=404)

        elif 'get_utilization_hours' in request.path:
            current_device_id = request.GET.get('deviceID')
            try:
                device_object = tracker_device.objects.get(device_id=current_device_id)
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=7)
                utilization_hours = {}

                for day in range(7):
                    current_date = start_date + timedelta(days=day)
                    
                    gps_data = GPSData.objects.filter(device_id=device_object, date=current_date).order_by('time')

                    state_hours = [0, 0, 0]

                    last_time = datetime.combine(current_date, datetime.min.time())
                    for state in range(1, 4):
                        state_data = gps_data.filter(state=state)
                        for data_point in state_data:
                            current_time = datetime.combine(current_date, data_point.time)
                            difference_seconds = (current_time - last_time).total_seconds()
                            if difference_seconds > 0:  
                                state_hours[state - 1] += difference_seconds
                            last_time = current_time

                    total_state_hours = sum(state_hours)
                    if total_state_hours > 86400:  
                        state_hours = [hour * 86400 / total_state_hours for hour in state_hours]
                    total_utilization = sum(state_hours) / 3600
                    utilization_hours[current_date.strftime('%A')] = {
                        "Inactive": state_hours[0] / 3600,  
                        "Idle": state_hours[1] / 3600,
                        "Active": state_hours[2] / 3600,
                        'Total':total_utilization 
                    }
         
                return JsonResponse(utilization_hours)

            except tracker_device.DoesNotExist:
                return JsonResponse({"error": "Device not found"}, status=404)
            
        elif 'search_data' in request.path:
            if request.method == 'GET':
                currentDeviceID = request.GET.get('deviceID')
                from_date = datetime.strptime(request.GET.get('fromDate'), '%Y-%m-%d').date()
                to_date = datetime.strptime(request.GET.get('toDate'), '%Y-%m-%d').date()

                utilization_hours = get_utilization_hours_for_report(currentDeviceID, from_date, to_date)

                deviceObject = tracker_device.objects.get(device_id=currentDeviceID)
                gps_data = GPSData.objects.filter(device_id=deviceObject, date__range=[from_date, to_date])
                ext_data = EXTData.objects.filter(device_id=deviceObject, date__range=[from_date, to_date])

                data = []

                for date in set(gps_data.values_list('date', flat=True)) | set(ext_data.values_list('date', flat=True)):
                    gps_distance = gps_data.filter(date=date).aggregate(Sum('distance'))['distance__sum'] or 0
                    ext_distance = ext_data.filter(date=date).aggregate(Sum('distance'))['distance__sum'] or 0
                    watt_hr = ext_data.filter(date=date).aggregate(Sum('watt_hr'))['watt_hr__sum'] or 0

                    data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'gps_distance': gps_distance,
                        'ext_distance': ext_distance,
                        'watt_hr': watt_hr,
                        'utilization_hours': utilization_hours.get(date.strftime('%A'), {})
                    })

                return JsonResponse(data, safe=False)
            
        if 'generate-pdf' in request.path:
            currentDeviceID = request.GET.get('deviceID')
            fromDate = request.GET.get('fromDate')
            toDate = request.GET.get('toDate')

            try:
                deviceObject = tracker_device.objects.get(device_id=currentDeviceID)
                utilization_hours = self.get_utilization_hours_for_report(currentDeviceID, fromDate, toDate)
                gps_data = GPSData.objects.filter(device_id=deviceObject, date__range=[fromDate, toDate])
                ext_data = EXTData.objects.filter(device_id=deviceObject, date__range=[fromDate, toDate])
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="Forklift.pdf"'
                pdf = SimpleDocTemplate(response, pagesize=letter)
                styles = getSampleStyleSheet()
                center_style = ParagraphStyle(name='Center', parent=styles['Normal'], alignment=1)
                content = []
                title = Paragraph("<b>INNOSPACE</b><br/><br/>", center_style)
                content.append(title)
                content.append(Spacer(1, 0.2 * inch))
                phone_email = Paragraph("<b>Phone:</b> +91-44-45550419<br/><b>Email:</b> info@innospace.co.in", styles['Normal'])
                content.append(phone_email)
                content.append(Spacer(1, 0.5 * inch))
                table_data = [['Date', 'GPS Distance', 'ODOMETER Distance', 'Watt HR', 'Utilization Hours']]

                for date in set(gps_data.values_list('date', flat=True)) | set(ext_data.values_list('date', flat=True)):
                    gps_distance = gps_data.filter(date=date).aggregate(Sum('distance'))['distance__sum'] or 0
                    ext_distance = ext_data.filter(date=date).aggregate(Sum('distance'))['distance__sum'] or 0
                    watt_hr = ext_data.filter(date=date).aggregate(Sum('watt_hr'))['watt_hr__sum'] or 0

                    active_hours = utilization_hours.get(date.strftime('%A'), {}).get('Active', 0)
                    inactive_hours = utilization_hours.get(date.strftime('%A'), {}).get('Inactive', 0)
                    idle_hours = utilization_hours.get(date.strftime('%A'), {}).get('Idle', 0)

                    table_data.append([
                        date.strftime('%Y-%m-%d'),
                        gps_distance,
                        ext_distance,
                        watt_hr,
                        f"Active: {active_hours:.2f} Inactive: {inactive_hours:.2f} Idle: {idle_hours:.2f}"
                    ])
                table = Table(table_data)
                style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ])
                table.setStyle(style)
                content.append(table)
                pdf.build(content)

                return response

            except tracker_device.DoesNotExist:
                return JsonResponse({"error": "Device not found"}, status=404)
            
        if 'generate-csv' in request.path:
            device_id = request.GET.get('deviceID')
            from_date = request.GET.get('fromDate')
            to_date = request.GET.get('toDate')

            try:
                device_object = tracker_device.objects.get(device_id=device_id)
            except tracker_device.DoesNotExist:
                return HttpResponse("Device not found", status=404)
            from_date = datetime.strptime(from_date, "%Y-%m-%d")
            to_date = datetime.strptime(to_date, "%Y-%m-%d")
            utilization_hours = get_utilization_hours_for_report(device_id, from_date, to_date)
            gps_data = GPSData.objects.filter(device_id=device_object, date__range=[from_date, to_date])
            ext_data = EXTData.objects.filter(device_id=device_object, date__range=[from_date, to_date])
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="report.csv"'

            writer = csv.writer(response)
            writer.writerow(['Date', 'GPS Distance', 'ODOMETER Distance', 'Watt HR', 'Active Hours', 'Inactive Hours', 'Idle Hours'])

            for date in set(gps_data.values_list('date', flat=True)) | set(ext_data.values_list('date', flat=True)):
                formatted_date = date.strftime('%Y-%m-%d') 

            for date in set(gps_data.values_list('date', flat=True)) | set(ext_data.values_list('date', flat=True)):
                gps_distance = gps_data.filter(date=date).aggregate(Sum('distance'))['distance__sum'] or 0
                ext_distance = ext_data.filter(date=date).aggregate(Sum('distance'))['distance__sum'] or 0
                watt_hr = ext_data.filter(date=date).aggregate(Sum('watt_hr'))['watt_hr__sum'] or 0

                active_hours = utilization_hours.get(date.strftime('%A'), {}).get('Active', 0)
                inactive_hours = utilization_hours.get(date.strftime('%A'), {}).get('Inactive', 0)
                idle_hours = utilization_hours.get(date.strftime('%A'), {}).get('Idle', 0)

                writer.writerow([date, gps_distance, ext_distance, watt_hr, active_hours, inactive_hours, idle_hours])

            return response
            
            
    def get_utilization_hours_for_report(self, deviceId, fromdate, todate):
        try:
            deviceObject = tracker_device.objects.get(device_id=deviceId)
        except tracker_device.DoesNotExist:
            return {"error": "Device not found"}

        from_date = datetime.strptime(fromdate, '%Y-%m-%d').date()
        to_date = datetime.strptime(todate, '%Y-%m-%d').date()

        utilization_hours = {}

        for day in range((to_date - from_date).days + 1):
            current_date = from_date + timedelta(days=day)
            gps_data = GPSData.objects.filter(device_id=deviceObject, date=current_date).order_by('time')

            state_hours = [0, 0, 0]

            last_time = datetime.combine(current_date, datetime.min.time())
            for state in range(1, 4):
                state_data = gps_data.filter(state=state)
                for data_point in state_data:
                    current_time = datetime.combine(current_date, data_point.time)
                    difference_seconds = (current_time - last_time).total_seconds()
                    if difference_seconds > 0:
                        state_hours[state - 1] += difference_seconds
                    last_time = current_time

            total_state_hours = sum(state_hours)
            if total_state_hours > 86400:
                state_hours = [hour * 86400 / total_state_hours for hour in state_hours]
            total_utilization = sum(state_hours) / 3600
            utilization_hours[current_date.strftime('%A')] = {
                "Inactive": state_hours[0] / 3600,
                "Idle": state_hours[1] / 3600,
                "Active": state_hours[2] / 3600,
                'Total': total_utilization
            }

        return utilization_hours


    def post(self, request):
        data = JSONParser().parse(request)
        current_device_id = data.get('deviceID')
        if not current_device_id:
            return JsonResponse({'error': 'Device ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            device_object = tracker_device.objects.get(device_id=current_device_id)
        except tracker_device.DoesNotExist:
            return JsonResponse({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        if 'ext-data' in request.path:
            serializer = EXTDataSerializer(data=data)
        elif 'gps-data' in request.path:
            data['device_id'] = device_object.id
            serializer = GPSDataSerializer(data=data)
        else:
            return HttpResponse(status=404)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)