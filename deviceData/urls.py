from django.urls import path
from .views import views, ext_data_list, gps_data_list, get_gps_data

urlpatterns = [
    path('ext-data/', ext_data_list, name='ext-data-list'),
    path('gps-data/', gps_data_list, name='gps-data-list'),
    path('api/get_last_data/', views.get_last_data, name='get_last_data'),
    path('get_gps_data/', get_gps_data, name='get_gps_data'),
]
