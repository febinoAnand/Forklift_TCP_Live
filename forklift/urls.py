from django.urls import path
from .views import loginView, deviceDashborad, updateGPSTableView,updateEXTTableView


urlpatterns = [
    path('',loginView),
    path('devicedashboard',deviceDashborad),
    path('updategpstable',updateGPSTableView),
    path('updateexttable',updateEXTTableView),
]
