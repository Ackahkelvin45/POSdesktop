from channels.generic.websocket import AsyncWebsocketConsumer
import json
from datetime import timedelta
from django.utils import timezone
from asgiref.sync import sync_to_async


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("notifications", self.channel_name)
        print(f"Added to notifications group: {self.channel_name}")  # Debug log
        await self.accept()
        await self.send_missed_notifications()


    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard("notifications", self.channel_name)

    async def notify(self, event):
        # Send message to WebSocket
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))



    async def send_missed_notifications(self):
        from notifications.models import Notification
        
        # Fetch notifications asynchronously
        notifications = await sync_to_async(
            lambda: list(Notification.objects.filter(
                created_at__gte=timezone.now() - timedelta(seconds=20)
            ).order_by('-created_at'))
        )()

        # Debug log to confirm fetched notifications
        print(f"Found {len(notifications)} missed notifications")
        
        # Send each notification
        for notification in notifications:
            await self.send(text_data=json.dumps({
                'message': notification.message,
                'title': notification.title,
                'timestamp':notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }))