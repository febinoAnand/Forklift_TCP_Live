from django.urls import path
from .views import ext_data_list, gps_data_list

urlpatterns = [
    path('ext-data/', ext_data_list, name='ext-data-list'),
    path('gps-data/', gps_data_list, name='gps-data-list'),
]
