from django.db import models
from django.utils.timezone import now
from product.models import Product

saleStatus = (
    ("Completed", "Completed"),
    ("Paused", "Paused"),
    ("Cancelled", "Cancelled"),
)

class Sale(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the sale was made")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time when the sale record was last updated")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Total revenue for the sale")
    products = models.ManyToManyField('product.Product', through='SaleProduct', related_name='sales', help_text="Products involved in this sale")
    status = models.CharField(max_length=100, null=True, blank=True, help_text="Status of the sale", choices=saleStatus)
    cashier_name = models.CharField(max_length=255, null=True, blank=True, help_text="Cashier's name")
    sale_code=models.CharField(max_length=20,null=True, blank=True)

    def __str__(self):
        return f"Sale #{self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def calculate_total_amount(self):
        """Calculate the total amount of the sale based on SaleProduct subtotals."""
        total = sum(item.subtotal() for item in self.saleproduct_set.all())
        self.total_amount = total
        self.save()

    def complete_sale(self):
        """
        Mark the sale as completed and reduce the available quantity of products.
        """
        if self.status == "Completed":
            raise ValueError("This sale is already completed.")

        # Update product stock quantities
        for sale_product in self.saleproduct_set.all():
            product = sale_product.product
            if product.available_quantity < sale_product.quantity:
                raise ValueError(f"Not enough stock for {product.name}. Available: {product.available_quantity}, Required: {sale_product.quantity}")

            product.available_quantity -= sale_product.quantity
            product.save()

        # Update the status to Completed
        self.status = "Completed"
        self.save()



class SaleProduct(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, help_text="The associated sale")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text="The associated product")
    quantity = models.PositiveIntegerField(help_text="Quantity of the product sold")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Unit selling price at the time of sale")

    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.name} - {self.quantity} @ {self.unit_price}"

