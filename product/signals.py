from django.dispatch import Signal
from django.dispatch import receiver
from .models import Product
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from  notifications.models import Notification
from django.db.models.signals import pre_save, post_save


# Define the signal
reset_quantities_signal = Signal()
delete_quantities_signal = Signal()
delete_all_category_signal = Signal()




@receiver(pre_save, sender=Product)
def track_previous_quantity(sender, instance, **kwargs):
    """Track the previous available_quantity value before saving."""
    if instance.pk:  # Only for updates (not creation)
        try:
            # Get the previous state of the object
            instance.previous_available_quantity = Product.objects.get(pk=instance.pk).available_quantity
        except Product.DoesNotExist:
            instance.previous_available_quantity = None

@receiver(post_save, sender=Product)
def check_quantity(sender, instance, **kwargs):
    """Check and send notification if available_quantity changes and is <= 10."""
    # Only proceed if available_quantity has changed
    if hasattr(instance, 'previous_available_quantity') and instance.available_quantity != instance.previous_available_quantity:
        if instance.available_quantity <= 10:
            # Create the notification object
            notification = Notification.objects.create(
                message=f"The quantity of {instance.name} is low: {instance.available_quantity}",
                title='Low stock quantity',
            )

            # Send the notification to WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "notifications",  # Group name
                {
                    "type": "notify",
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "created_at": notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                },
            )
