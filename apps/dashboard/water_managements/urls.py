from .                      import views
from django.contrib         import admin
from django.urls            import include, path, re_path

app_name = "water_managements"

urlpatterns = [
    path(
        '<pk>', 
        views.WaterManagementList.as_view(), 
        name='water_management_list'
        ),
    path(
        '<fk>', 
        views.WaterManagementCreateView.as_view(), 
        name='water_management_create'
        ),    
]