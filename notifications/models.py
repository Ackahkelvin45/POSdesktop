from django.db import models

# Create your models here.



class Notification(models.Model):
    title=models.CharField(max_length=100,null=True)
    message = models.TextField( null=True, blank=True)
    is_read = models.BooleanField(default=False,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}: {self.message[:20]}"