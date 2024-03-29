from django.http import JsonResponse
from rest_framework import serializers
from .models import EXTData, GPSData
from .serializers import EXTDataSerializer, GPSDataSerializer
from .import views
from datetime import datetime, date ,time ,timedelta
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
    print("deviceId---->"+currentDeviceID)
    deviceObject = tracker_device.objects.get(device_id=currentDeviceID)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    utilization_hours = {}
    states = ["Inactive", "Idle", "Active"]

    for day in range(7):
        current_date = start_date + timedelta(days=day)
        gps_data = GPSData.objects.filter(device_id=deviceObject, date=current_date)
        
        state_hours = [0, 0, 0]

        last_time = datetime.combine(current_date, datetime.min.time())
        for state in range(1, 4):
            state_data = gps_data.filter(state=state).order_by("time")
            for data_point in state_data:
                current_time = datetime.combine(current_date, data_point.time)
                difference_seconds = (current_time - last_time).total_seconds()
                state_hours[state - 1] += difference_seconds
                last_time = current_time

        state_hours = [round(hours / 3600, 2) for hours in state_hours]
        print("state hours--->",state_hours)
        total_utilization = sum(state_hours)

        utilization_hours[current_date.strftime('%A')] = {
            "Inactive": state_hours[0],
            "Idle": state_hours[1],
            "Active": state_hours[2],
            'Total': total_utilization
        }

    return JsonResponse(utilization_hours)

def search_data(request):
    currentDeviceID = request.GET.get('deviceID')
    if request.method == 'GET':
        from_date = request.GET.get('fromDate')
        to_date = request.GET.get('toDate')
        gps_data = GPSData.objects.filter(date__range=[from_date, to_date])
        ext_data = EXTData.objects.filter(date__range=[from_date, to_date])
        
        data = []
        
        for date in set(gps_data.values_list('date', flat=True)) | set(ext_data.values_list('date', flat=True)):
            gps_distance = gps_data.filter(date=date).aggregate(Sum('distance'))['distance__sum'] or 0
            ext_distance = ext_data.filter(date=date).aggregate(Sum('distance'))['distance__sum'] or 0
            watt_hr = ext_data.filter(date=date).aggregate(Sum('watt_hr'))['watt_hr__sum'] or 0
            
            data.append({
                'date': date,
                'gps_distance': gps_distance,
                'ext_distance': ext_distance,
                'watt_hr': watt_hr,
            })

        return JsonResponse(data, safe=False)

def generate_pdf(request):
    currentDeviceID = request.GET.get('deviceID')
    response = get_utilization_hours(request)
    utilization_hours = json.loads(response.content)

    all_dates = set(GPSData.objects.values_list('date', flat=True).distinct()) | \
                set(EXTData.objects.values_list('date', flat=True).distinct())
    ext_data = EXTData.objects.all()

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

    table_data = [['Date', 'GPS Distance', 'EXT Distance', 'Watt HR', 'Active Hours']]

    for date in all_dates:
        gps_entries = GPSData.objects.filter(date=date)
        ext_entry = ext_data.filter(date=date).first()

        if gps_entries.exists():
            gps_entry = gps_entries.first()
            gps_distance = gps_entry.distance
        else:
            gps_distance = "N/A"

        if ext_entry:
            ext_distance = ext_entry.distance
            watt_hr = ext_entry.watt_hr
        else:
            ext_distance = "N/A"
            watt_hr = "N/A"

        active_hours = utilization_hours.get(date.strftime('%A'), {}).get('Active', 0)
        
        table_data.append([
            date.strftime('%Y-%m-%d'),
            gps_distance,
            ext_distance,
            watt_hr,
            active_hours
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
    currentDeviceID = request.GET.get('deviceID')
    response = get_utilization_hours(request)
    utilization_hours = json.loads(response.content)
    
    all_dates = set(GPSData.objects.values_list('date', flat=True).distinct()) | \
                set(EXTData.objects.values_list('date', flat=True).distinct())
    ext_data = EXTData.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Forklift.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'GPS Distance', 'EXT Distance', 'Watt HR', 'Active Hours'])

    for date in all_dates:
        gps_entries = GPSData.objects.filter(date=date)
        ext_entry = ext_data.filter(date=date).first()

        if gps_entries.exists():
            gps_entry = gps_entries.first()
            gps_distance = gps_entry.distance
        else:
            gps_distance = "N/A"

        if ext_entry:
            ext_distance = ext_entry.distance
            watt_hr = ext_entry.watt_hr
        else:
            ext_distance = "N/A"
            watt_hr = "N/A"

        active_hours = utilization_hours.get(date.strftime('%A'), {}).get('Active', 0)
        
        writer.writerow([
            date.strftime('%Y-%m-%d'),
            gps_distance,
            ext_distance,
            watt_hr,
            active_hours
        ])

    return response