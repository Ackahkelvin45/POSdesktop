# Generated by Django 5.1.2 on 2024-12-07 07:06

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0008_product_units_per_bulk_delete_inventorylog'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('add', 'Stock Added'), ('remove', 'Stock Removed'), ('adjust', 'Stock Adjusted'), ('sale', 'Product Sold')], help_text='The type of action (add, remove, adjust, sale)', max_length=10)),
                ('quantity', models.PositiveIntegerField(help_text='The quantity of product added, removed, or sold')),
                ('previous_quantity', models.PositiveIntegerField(blank=True, help_text='The stock quantity before this action was performed', null=True)),
                ('new_quantity', models.PositiveIntegerField(blank=True, help_text='The stock quantity after this action was performed', null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, help_text='The price of the product at the time of the action (if applicable)', max_digits=10, null=True)),
                ('total_value', models.DecimalField(blank=True, decimal_places=2, help_text='The total value of the action (quantity * price)', max_digits=10, null=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time when the stock action occurred.')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date and time when the log entry was created.')),
                ('notes', models.TextField(blank=True, help_text='Any additional notes regarding the inventory action', null=True)),
                ('product', models.ForeignKey(help_text='The product for which the stock change is recorded.', on_delete=django.db.models.deletion.CASCADE, related_name='inventory_logs', to='product.product')),
            ],
        ),
    ]
