from django.urls import path
from .views import GlobalActivityLogListView

app_name = 'activities'


urlpatterns = [
    path('list/', GlobalActivityLogListView.as_view(), name='global_activity_logs'),
]