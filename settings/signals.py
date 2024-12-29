# signals.py
from django.db import transaction
from .models import Settings

def create_settings_object(sender, **kwargs):
    """
    Ensure a default Settings object is created after migrations.
    """
    with transaction.atomic():
        if not Settings.objects.exists():
            Settings.objects.create()
