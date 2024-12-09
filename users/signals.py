from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group

@receiver(post_migrate)
def create_roles(sender, **kwargs):
    # Create the "cashier" group if it doesn't exist
    Group.objects.get_or_create(name='cashier')
    # Create the "manager" group if it doesn't exist
    Group.objects.get_or_create(name='manager')
    Group.objects.get_or_create(name='admin')
