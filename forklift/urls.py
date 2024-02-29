from django.urls import path
from .views import loginView, deviceDashborad, updateGPSTableView,updateEXTTableView,report_page_view


urlpatterns = [
    path('',loginView),
    path('devicedashboard',deviceDashborad),
    path('updategpstable',updateGPSTableView),
    path('updateexttable',updateEXTTableView),
    path('reportpage/', report_page_view, name='report_page'),
]