from django.urls import path
from .views import loginView, deviceDashborad, historypage,get_gps_data_for_date,updateGPSTabledateView,updateEXTTabledateView , updateGPSTableView,updateEXTTableView, report_page_view, register_device ,list_page_view, tracker_device_list,logoutView


urlpatterns = [
    path('',loginView, name='login'),
    path('login',loginView, name='login'),
    path('devicedashboard',deviceDashborad, name='device_dashboard'),
    path('updategpstable',updateGPSTableView, name='update_gpstable'),
    path('updateexttable',updateEXTTableView, name='update_exttable'),
    path('reportpage/', report_page_view, name='report_page'),
    path('register/', register_device, name='register_device'),
    path('listpage/', list_page_view, name='list_page'),
    path('listpage/api/tracker-devices/', tracker_device_list, name='tracker-device-list'),
    path('logout',logoutView,name='logoutView'),
    path('historypage',historypage, name='history_page'),
    path('get_gps_data_for_date/', get_gps_data_for_date, name='get_gps_data_for_date'),
    path('updateextdatetable',updateEXTTabledateView, name='update_exttabledate'),
    path('updategpsdatetable',updateGPSTabledateView, name='update_gpsdatetable'),
]
