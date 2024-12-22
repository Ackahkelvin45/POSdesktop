from django.urls import path 
from .views import NotificationAPIView, NotificationsList,MarkAsReadView

app_name = 'notifications'

urlpatterns = [
    path('list/', NotificationAPIView.as_view(), name='notification_list'),
    path('all/', NotificationsList.as_view(), name='notificationsall'),
        path('notifications/mark-as-read/', MarkAsReadView.as_view(), name='mark_as_read'),
]