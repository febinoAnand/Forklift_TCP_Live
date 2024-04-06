from django.urls import path
from .views import views, ext_data_list, gps_data_list, get_today_gps_data,get_last_date_data, get_gps_date_data, gps_data_date_list,ext_data_date_list, get_utilization_date_hours, get_utilization_hours , get_gps_data, search_data, generate_pdf,generate_csv

urlpatterns = [
    path('ext-data/', ext_data_list, name='ext-data-list'),
    path('gps-data/', gps_data_list, name='gps-data-list'),
    path('api/get_last_data/', views.get_last_data, name='get_last_data'),
    path('api/get-gps-data/', get_gps_data, name='get_gps_data'),
    path('get_today_gps_data/', get_today_gps_data, name='get_today_gps_data'),
    path('get_utilization_hours/', get_utilization_hours, name='get_utilization_hours'),
    path('search_data/', search_data, name='search_data'),
    path('generate-pdf/', generate_pdf, name='generate_pdf'),
    path('generate-csv/', generate_csv, name='generate_csv'),
    path('get-gps-date-data/', get_gps_date_data, name='get_gps_date_data'),
    path('get_utilization_date_hours/', get_utilization_date_hours, name='get_utilization_date_hours'),
    path('ext-date-data/', ext_data_date_list, name='ext-data-date-list'),
    path('gps-date-data/', gps_data_date_list, name='gps_data_date_list'),
    path('get_last_date_data/', get_last_date_data, name='get_last_date_data'),
]
