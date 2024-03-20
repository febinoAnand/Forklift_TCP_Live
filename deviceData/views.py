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

    utilization_hours = {}
    for day in range(7):
        current_date = start_date + timedelta(days=day)
        gps_data = GPSData.objects.filter(date=current_date)
        
        active_hours = gps_data.filter(state=3).aggregate(
            total_hours=Sum(
                (F('time__hour') + (F('time__minute') / 60)) - 0.5,
                output_field=DecimalField()
            )
        )['total_hours'] or 0
        
        inactive_hours = gps_data.filter(state=1).aggregate(
            total_hours=Sum(
                (F('time__hour') + (F('time__minute') / 60)) - 0.5,
                output_field=DecimalField()
            )
        )['total_hours'] or 0
        
        idle_hours = gps_data.filter(state=2).aggregate(
            total_hours=Sum(
                (F('time__hour') + (F('time__minute') / 60)) - 0.5,
                output_field=DecimalField()
            )
        )['total_hours'] or 0

        utilization_hours[current_date.strftime('%A')] = {
            'Active': active_hours,
            'Inactive': inactive_hours,
            'Idle': idle_hours
        }

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