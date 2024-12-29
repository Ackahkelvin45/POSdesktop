from django.db import models
from django.utils.timezone import now
from product.models import Product
import random
import string
import datetime

saleStatus = (
    ("Completed", "Completed"),
    ("Paused", "Paused"),
    ("Cancelled", "Cancelled"),
)

def generate_unique_sale_code():
        """
        Generate a unique sale code consisting of random alphanumeric characters,
        combined with the current timestamp to ensure uniqueness.
        """
        # Generate random letters (upper case)
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        
        # Generate random digits (e.g., 4 digits)
        digits = ''.join(random.choices(string.digits, k=4))
        
        # Get the current date and time to append to the code
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Combine everything into a unique code
        sale_code = f"{letters}{digits}{timestamp}"

        return sale_code

class Sale(models.Model):
    created_at = models.DateTimeField( help_text="Date and time when the sale was made")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time when the sale record was last updated")
    total_amount = models.DecimalField(max_digits=40, decimal_places=2, default=0.00, help_text="Total revenue for the sale")
    products = models.ManyToManyField('product.Product', through='SaleProduct', related_name='sales', help_text="Products involved in this sale")
    status = models.CharField(max_length=100, null=True, blank=True, help_text="Status of the sale", choices=saleStatus)
    cashier_name = models.CharField(max_length=255, null=True, blank=True, help_text="Cashier's name")
    sale_code=models.CharField(max_length=20,null=True, blank=True,unique=True)
    payment_type=models.CharField(max_length=100,null=True, blank=True)
    amount_paid=models.DecimalField(max_digits=40,null=True, blank=True,decimal_places=2, default=0.00)
    balance=models.DecimalField(max_digits=40,null=True, blank=True,decimal_places=2, default=0.00)
    total_profit=models.DecimalField(max_digits=40,null=True, blank=True,decimal_places=2, default=0.00,)


    def save(self, *args, **kwargs):
        # Automatically generate a unique sale code before saving the sale
        if not self.sale_code:
            self.sale_code = generate_unique_sale_code()
        
        
        
           

        super().save(*args, **kwargs)
    def __str__(self):
        return f"Sale #{self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    
    def calculate_total_profit(self):
        """
        Calculate the total profit for the sale.
        Profit is calculated as the difference between the selling price and the cost price.
        """
        total_profit = 0
        for sale_product in self.saleproduct_set.all():
           
            profit = (sale_product.unit_selling_price - sale_product.unit_cost_price) * sale_product.quantity
            total_profit += profit
            self.total_profit=total_profit
            self.save()
        return total_profit

    def calculate_total_amount(self):
        """Calculate the total amount of the sale based on SaleProduct subtotals."""
        total = sum(item.subtotal() for item in self.saleproduct_set.all())
        self.total_amount = total
        self.save()

    def complete_sale(self):
        """
        Mark the sale as completed and reduce the available quantity of products.
        If any product has insufficient stock, revert all previously subtracted quantities.
        """
        if self.status == "Completed":
            raise ValueError("This sale is already completed.")

        # List to hold products to rollback if needed
        products_to_rollback = []

        # Check stock for each product in the sale
        for sale_product in self.saleproduct_set.all():
            product = sale_product.product
            if product.available_quantity < sale_product.quantity:
                # Not enough stock, rollback all changes made so far
                for prod_to_rollback in products_to_rollback:
                    # Restore previously subtracted product quantities
                    prod_to_rollback['product'].available_quantity += prod_to_rollback['quantity']
                    prod_to_rollback['product'].save()
                raise ValueError(f"Not enough stock for {product.name}. Available: {product.available_quantity}, Required: {sale_product.quantity}")

            # If stock is sufficient, reduce the product stock
            product.available_quantity -= sale_product.quantity
            product.save()

            # Add to the rollback list in case we need to undo this later
            products_to_rollback.append({
                'product': product,
                'quantity': sale_product.quantity
            })

        # If everything is okay, mark the sale as completed
        self.status = "Completed"
        self.save()


class SaleProduct(models.Model):
    SALE_TYPE_CHOICES = (
        ("Unit", "Unit"),
        ("Bulk", "Bulk"),
    )

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, help_text="The associated sale")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text="The associated product")
    quantity = models.PositiveIntegerField(help_text="Quantity of the product sold")
    unit_cost_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Unit selling price at the time of sale",null=True)
    unit_selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="unit Selling price at the time of sale",null=True, default=0.00)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="bulk price at the time of sale",null=True)
    bulk_selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling price  for bulk at the time of sale", default=0.00,null=True)
    total = models.DecimalField(max_digits=15, decimal_places=2, help_text="Total amount for this product in the sale", default=0.00,null=True)
    sale_type = models.CharField(
        max_length=10, 
        choices=SALE_TYPE_CHOICES, 
        default="Unit", 
        help_text="Type of the sale (Unit or Bulk)"
    )

    def subtotal(self):
        """Calculate the subtotal for this product in the sale."""
        if self.sale_type=="Unit":
            return self.quantity * self.unit_selling_price
        else:
            return  self.quantity * self.unit_selling_price

    def __str__(self):
        return f"{self.product.name} - {self.quantity}  ({self.sale_type})"

