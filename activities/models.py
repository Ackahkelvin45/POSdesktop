from django.db import models
from authentication.models import CustomUser
from django.utils.timezone import now

class GlobalActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('reverse', 'Reverse'),
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, help_text="User who performed the action")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, help_text="Type of action performed")
    model_name = models.CharField(max_length=50, help_text="Name of the model affected")
    notes = models.TextField(blank=True, help_text="Optional notes about the action")
    timestamp = models.DateTimeField(default=now, help_text="Time when the action occurred")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} (ID: {self.object_id})"
