from django.apps import AppConfig
from django.db.models.signals import post_migrate


class SettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settings'


    def ready(self):
        from .signals import create_settings_object
        post_migrate.connect(create_settings_object, sender=self)