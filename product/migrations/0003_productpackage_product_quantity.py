# Generated by Django 5.1.2 on 2024-11-22 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='productpackage',
            name='product_quantity',
            field=models.PositiveIntegerField(default=0, help_text='Total quantity of the  products in the package available', null=True),
        ),
    ]
