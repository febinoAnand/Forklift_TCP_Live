from django.urls import path
from .views import AllDeviceClass, loginView, deviceDashborad, historypage,get_gps_data_for_date, get_state_data, updateGPSTabledateView,updateEXTTabledateView , updateGPSTableView,updateEXTTableView, report_page_view, register_device ,list_page_view, tracker_device_list,logoutView


urlpatterns = [
    path('',loginView, name='login'),
    path('login',loginView, name='login'),
    path('devicedashboard',AllDeviceClass.as_view(), name='device_dashboard'),
    path('updategpstable', AllDeviceClass.as_view(), name='update_gpstable'),
    path('updateexttable', AllDeviceClass.as_view(), name='update_exttable'),
    path('reportpage/', AllDeviceClass.as_view(), name='report_page'),
    path('listpage/api/tracker-devices/', AllDeviceClass.as_view(), name='tracker_devices_api'),
    path('register/', AllDeviceClass.as_view(), name='register_device'),
    path('listpage/', AllDeviceClass.as_view(), name='list_page'),
    path('logout',logoutView,name='logoutView'),
    path('historypage',AllDeviceClass.as_view(), name='history_page'),
    path('get_gps_data_for_date/', AllDeviceClass.as_view(), name='get_gps_data_for_date'),
    path('updateextdatetable',AllDeviceClass.as_view(), name='update_exttabledate'),
    path('updategpsdatetable',AllDeviceClass.as_view(), name='update_gpsdatetable'),
    path('get_state_data/', get_state_data, name='get_state_data'),
]
