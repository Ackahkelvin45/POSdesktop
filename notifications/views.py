from django.http import JsonResponse
from django.views import View
from .models import Notification
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
class NotificationAPIView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        # Fetch notifications for the logged-in user
        notifications = Notification.objects.filter(is_read=False).order_by('-created_at')
        total_count = notifications.count()

        # Format notifications for JSON response
        notifications_data = [
            {
                'id': notification.id,
                'message': notification.message,
                "title":notification.title,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for notification in notifications
        ]

        return JsonResponse({
            'notifications': notifications_data,
            'total_count': total_count,
        })
        
class NotificationsList(LoginRequiredMixin,ListView):
    model = Notification
    template_name = 'notifications/notificationlist.html'
    context_object_name = 'notifications'
    ordering = ['-created_at']  


class MarkAsReadView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(is_read=False).update(is_read=True)
        return JsonResponse({"status": "success", "message": "Notifications marked as read"})