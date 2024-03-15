from django.urls import path
from .views import loginView, deviceDashborad, updateGPSTableView,updateEXTTableView, report_page_view, register_device ,list_page_view, tracker_device_list


urlpatterns = [
    path('',loginView, name='login'),
    path('devicedashboard',deviceDashborad),
    path('updategpstable',updateGPSTableView),
    path('updateexttable',updateEXTTableView),
    path('reportpage/', report_page_view, name='report_page'),
    path('register/', register_device, name='register_device'),
    path('listpage/', list_page_view, name='list_page'),
    path('listpage/api/tracker-devices/', tracker_device_list, name='tracker-device-list'),
]
