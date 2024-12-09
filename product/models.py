from django.db import models

# Create your models here.
class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True,null=True, help_text="Enter the product category (e.g., Dairy, Bakery, Beverages)")
    description = models.TextField(blank=True, null=True, help_text="Optional description for the category")

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100, help_text="Enter the product name",null=True)
    description = models.TextField(blank=True, null=True, help_text="Enter a brief description of the product (optional)")
    unit_selling_price = models.DecimalField(max_digits=10,null=True, decimal_places=2, help_text="Enter the selling product price")
    bulk_selling_price = models.DecimalField(max_digits=10,null=True, decimal_places=2, help_text="Enter the bulk selling product price")
    unit_cost_price = models.DecimalField(max_digits=10,null=True, decimal_places=2, help_text="Enter the cost  product price")
    bulk_cost_price = models.DecimalField(max_digits=10,null=True, decimal_places=2, help_text="Enter the bulk cost  product price")
    available_quantity = models.PositiveIntegerField(default=0,null=True, help_text="Enter the available quantity of the product")
    units_per_bulk = models.PositiveIntegerField(default=1,null=True, help_text="Enter the number of unit quantities that make up a bulk quantity")
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, related_name='products', help_text="Select a category for this product")
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, help_text="Upload an image of the product")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def is_low_stock(self):
        return self.quantity < 10  
    

class ProductPackage(models.Model):
    name = models.CharField(max_length=200,null=True,help_text="Enter the package name")
    description = models.TextField(blank=True,  null=True, help_text="Description of the package (optional)")
    product = models.ForeignKey(Product,null=True, on_delete=models.CASCADE, related_name='package_items')
    package_price = models.DecimalField(max_digits=10,null=True, decimal_places=2, help_text="Enter the price for the entire package")
    quantity = models.PositiveIntegerField(default=0,null=True, help_text="Total quantity of the package available")
    product_quantity = models.PositiveIntegerField(default=0,null=True, help_text="Total quantity of the  products in the package available")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name