from django.urls import path 
from . import views 
app_name="settings"


urlpatterns = [
    path('edit/', views.edit_settings, name='edit_settings'),
        path('settings/get/', views.GetSettingsView.as_view(), name='get-settings'),

]