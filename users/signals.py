from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

@receiver(post_migrate)
def create_roles(sender, **kwargs):
    # Create the "cashier" group if it doesn't exist
    cashier_group, created = Group.objects.get_or_create(name='cashier')

    # Create the "manager" group if it doesn't exist
    manager_group, created = Group.objects.get_or_create(name='manager')

    # Create the "admin" group if it doesn't exist
    admin_group, created = Group.objects.get_or_create(name='admin')

    if created:
        # Assign all permissions to the "admin" group
        all_permissions = Permission.objects.all()
        admin_group.permissions.set(all_permissions)
