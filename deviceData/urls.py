from django.urls import path
from .views import views, ext_data_list, gps_data_list, get_today_gps_data, utilization_data , get_gps_data, search_data, generate_pdf,generate_csv

urlpatterns = [
    path('ext-data/', ext_data_list, name='ext-data-list'),
    path('gps-data/', gps_data_list, name='gps-data-list'),
    path('api/get_last_data/', views.get_last_data, name='get_last_data'),
    path('api/get-gps-data/', get_gps_data, name='get_gps_data'),
    path('get_today_gps_data/', get_today_gps_data, name='get_today_gps_data'),
    path('utilization-data/', utilization_data, name='utilization_data'),
    path('search_data/', search_data, name='search_data'),
    path('generate-pdf/', generate_pdf, name='generate_pdf'),
    path('generate-csv/', generate_csv, name='generate_csv'),
]
