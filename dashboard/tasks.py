# connectivity/tasks.py
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging
from .services import check_internet_connection

logger = logging.getLogger(__name__)

@shared_task
def periodic_internet_check():
    is_connected = check_internet_connection()
    
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'connectivity_group', 
            {
                'type': 'send_connectivity_status',
                'is_connected': is_connected
            }
        )
        logger.info(f"Internet check broadcast: {is_connected}")
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
    
    return is_connected