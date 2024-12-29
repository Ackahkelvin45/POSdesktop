from django.db import models

# Create your models here.

class Settings(models.Model):
    change_date = models.BooleanField(default=False,null=True)
    always_print_receipt=models.BooleanField(default=False,null=True)
    change_date_sale = models.BooleanField(default=False,null=True)
    
    
    def __str__(self):
        return "settigs"