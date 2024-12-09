# connectivity/consumers.py
import logging
import json
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class ConnectivityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('connectivity_group', self.channel_name)
        logger.info(f"WebSocket connected: {self.channel_name}")
        await self.accept()

    async def send_connectivity_status(self, event):
        try:
            message = json.dumps({
                'is_connected': event['is_connected']
            })
            logger.info(f"Sending message: {message}")
            await self.send(text_data=message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")