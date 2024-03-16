from django.http import JsonResponse
from rest_framework import serializers
from .models import EXTData, GPSData
from .serializers import EXTDataSerializer, GPSDataSerializer
from .import views
from datetime import datetime, date ,time ,timedelta
from django.db.models import Count ,Sum
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
import json
import csv
from django.http import HttpResponse
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,  Paragraph, Spacer

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
        .annotate(duration=Count('state'))

    response_data = []

    for item in data:
        response_data.append({
            'state': item['state'],
            'duration': item['duration']
        })

    return JsonResponse(response_data, safe=False)

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
    gps_dates = GPSData.objects.values_list('date', flat=True).distinct()
    ext_dates = EXTData.objects.values_list('date', flat=True).distinct()
    all_dates = set(gps_dates) | set(ext_dates)
    ext_data = EXTData.objects.all()

    table_data = [['Date', 'GPS Distance', 'EXT Distance', 'Watt HR']]

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

        table_data.append([
            date,
            gps_distance,
            ext_distance,
            watt_hr
        ])

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Forklift.pdf"'

    pdf = SimpleDocTemplate(response, pagesize=letter)

    styles = getSampleStyleSheet()
    center_style = ParagraphStyle(name='Center', parent=styles['Normal'], alignment=1)

    content = []

    title = Paragraph("<b>INNOSPACE</b><br/><br/>", center_style)
    content.append(title)
    content.append(Spacer(1, 0.2 * inch))
    address = Paragraph("<b>Address:</b><br/>Innospace Automation Services Pvt Ltd,<br/>Old no. 38, New no. 20/1, Vaigai colony,<br/>12th Avenue, Ashok Nagar,<br/>Chennai-600083.", styles['Normal'])
    content.append(address)
    phone_email = Paragraph("<b>Phone:</b> +91-44-45550419<br/><b>Email:</b> info@innospace.co.in", styles['Normal'])
    content.append(phone_email)
    content.append(Spacer(1, 0.5 * inch))

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
    gps_dates = GPSData.objects.values_list('date', flat=True).distinct()
    ext_dates = EXTData.objects.values_list('date', flat=True).distinct()
    all_dates = set(gps_dates) | set(ext_dates)
    ext_data = EXTData.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Forklift.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'GPS Distance', 'EXT Distance', 'Watt HR'])

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

        writer.writerow([
            date,
            gps_distance,
            ext_distance,
            watt_hr
        ])

    return response