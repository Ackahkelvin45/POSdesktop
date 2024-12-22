from django.shortcuts import render

from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404, redirect, render
from product.models import Product
from .models import Sale, SaleProduct
from django.http import JsonResponse
from django.http import JsonResponse
from django.views import View
from .models import Product
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.core.exceptions import ValidationError
from django.db import transaction


class ProductAutocompleteView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "")
        products = Product.objects.filter(name__icontains=query)[:10] if query else Product.objects.all()[:10]
        data = [{"id": product.id, "text": product.name, "price": str(product.unit_selling_price)} for product in products]
        return JsonResponse({"results": data})


class MakeSaleView(LoginRequiredMixin,TemplateView):
    template_name = "sales/makesale.html"

    def get(self, request, *args, **kwargs):
        # Display the form for making a sale
        return render(request, self.template_name, {"products": Product.objects.all()})








class ProductFilterView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        # Get the 'name' parameter directly from POST data
        name_query = request.POST.get('name', '').strip()
        
        # If no name is provided, return a specific message
        if not name_query:
            return JsonResponse({'message': 'Please enter a product name to search.'}, status=400)

        # Filter products by the 'name' field
        products = Product.objects.filter(name__icontains=name_query)

        # If no products are found, return a custom message
        if not products.exists():
            return JsonResponse({'message': 'No products found matching your query.'}, status=404)

        # Serialize the product objects into a list of dictionaries
        product_data = [{
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'unit_selling_price': str(product.unit_selling_price),
            'bulk_selling_price': str(product.bulk_selling_price),
            'unit_cost_price': str(product.unit_cost_price),
            'bulk_cost_price': str(product.bulk_cost_price),
            'available_quantity': product.available_quantity,
            'units_per_bulk': product.units_per_bulk,
            'category': product.category.name if product.category else '',
            'image': product.image.url if product.image else None,
            'created_at': product.created_at,
            'updated_at': product.updated_at,
        } for product in products]

        # Return the filtered data as a JSON response
        return JsonResponse({'products': product_data}, safe=False)


class PauseSaleView(View):
    """
    Class-based view to handle pausing an ongoing sale.
    Accepts POST requests with sale data and saves it with 'Paused' status.
    """
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            # Parse the sale data from request
            data = json.loads(request.body)
            products_data = data.get('products', [])
            sale_date = data.get('sale_date')
            
            if not products_data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No products provided for the sale'
                }, status=400)

            # Create a new sale instance
            sale = Sale.objects.create(
                status='Paused',
                cashier_name=request.user.first_name +" "+request.user.last_name,
            )

            # Process each product in the sale
            for product_data in products_data:
                product = get_object_or_404(Product, id=product_data['product_id'])
                quantity = int(product_data['quantity'])
                sale_type = product_data['sale_type']
                
                # Determine the correct price based on sale type
                unit_price = (
                    product.unit_cost_price 
                    if sale_type == 'Unit' 
                    else product.bulk_cost_price
                )

                # Create SaleProduct instance
                SaleProduct.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price
                )

            # Calculate the total amount
            sale.calculate_total_amount()

            return JsonResponse({
                'status': 'success',
                'message': 'Sale paused successfully',
                'sale_id': sale.id,
                'total_amount': str(sale.total_amount)
            })

        except ValidationError as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
            
        except Exception as e:
            # Log the error here if you have logging configured
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while pausing the sale'
            }, status=500)
