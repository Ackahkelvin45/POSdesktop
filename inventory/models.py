from django.db import models
from django.utils import timezone
from product.models import Product

class InventoryLog(models.Model):
    ACTION_CHOICES = [
        ('add', 'Stock Added'),
        ('remove', 'Stock Removed'),
        ('sale', 'Product Sold'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_logs', help_text="The product for which the stock change is recorded.")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, help_text="The type of action (add, remove, adjust, sale)")
    quantity = models.PositiveIntegerField(help_text="The quantity of product added, removed, or sold")
    previous_quantity = models.PositiveIntegerField(help_text="The stock quantity before this action was performed", blank=True, null=True)
    new_quantity = models.PositiveIntegerField(help_text="The stock quantity after this action was performed", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="The price of the product at the time of the action (if applicable)")
    total_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="The total value of the action (quantity * price)")
    action_date = models.DateTimeField(default=timezone.now, help_text="The date and time when the stock action occurred.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the log entry was created.")
    notes = models.TextField(blank=True, null=True, help_text="Any additional notes regarding the inventory action")

    def save(self, *args, **kwargs):
        # Get the current product instance
        product = self.product

        # Get the previous stock quantity from the database (before the action)
        self.previous_quantity = product.available_quantity

        # Determine the new stock quantity based on the action
        if self.action == 'add':
            self.new_quantity = self.previous_quantity + self.quantity
        elif self.action == 'remove' or self.action == 'adjust':
            self.new_quantity = self.previous_quantity - self.quantity
        elif self.action == 'sale':
            self.new_quantity = self.previous_quantity - self.quantity
        else:
            self.new_quantity = self.previous_quantity

        # Automatically calculate the total value if not set manually
        if self.price is not None and self.total_value is None:
            self.total_value = self.quantity * self.price
        
        # Save the log entry
        super().save(*args, **kwargs)

        # After saving the log, update the product's available quantity
        product.available_quantity = self.new_quantity
        product.save()

    def reverse_action(self):
        """
        Undo this log's action and delete the log.
        """
        product = self.product

        # Revert the product's available quantity
        if self.action == 'add':
            product.available_quantity -= self.quantity
        elif self.action == 'remove':
            product.available_quantity += self.quantity
        elif self.action == 'sale':
            product.available_quantity += self.quantity
        
        # Save the updated product quantity
        product.save()

        # Delete this log
        self.delete()

    def __str__(self):
        return f"{self.product.name} - {self.action} - {self.quantity} units"
