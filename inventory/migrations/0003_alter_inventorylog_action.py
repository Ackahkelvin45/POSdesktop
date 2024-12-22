# Generated by Django 5.1.2 on 2024-12-09 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_alter_inventorylog_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorylog',
            name='action',
            field=models.CharField(choices=[('add', 'Stock Added'), ('remove', 'Stock Removed'), ('sale', 'Product Sold'), ('updated manually(add)', 'Stock Added manually'), ('updated manually(remove)', 'Stock Removed manually')], help_text='The type of action (add, remove, adjust, sale)', max_length=30),
        ),
    ]