from django.urls import path
from .views import views,CombinedDataView, get_gps_date_data,get_today_gps_date_data, gps_data_date_list,ext_data_date_list, get_utilization_date_hours , get_gps_data, search_data, generate_pdf,generate_csv

urlpatterns = [
    path('ext-data/', CombinedDataView.as_view(), name='ext-data-list'),
    path('gps-data/', CombinedDataView.as_view(), name='gps-data-list'),
    path('api/get_last_data/', views.CombinedDataView.as_view(), name='get_last_data'),
    path('api/get-gps-data/', get_gps_data, name='get_gps_data'),
    path('get_today_gps_data/', CombinedDataView.as_view(), name='get_today_gps_data'),
    path('get_utilization_hours/', CombinedDataView.as_view(), name='get_utilization_hours'),
    path('search_data/', CombinedDataView.as_view(), name='search_data'),
    path('generate-pdf/', generate_pdf, name='generate_pdf'),
    path('generate-csv/', generate_csv, name='generate_csv'),
    path('get-gps-date-data/', get_gps_date_data, name='get_gps_date_data'),
    path('get_utilization_date_hours/', get_utilization_date_hours, name='get_utilization_date_hours'),
    path('ext-date-data/', ext_data_date_list, name='ext-data-date-list'),
    path('gps-date-data/', gps_data_date_list, name='gps_data_date_list'),
    path('get_today_gps_date_data/', get_today_gps_date_data, name='get_today_gps_date_data'),
]
