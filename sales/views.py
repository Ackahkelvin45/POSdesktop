from django.shortcuts import render

from django.views.generic import TemplateView, View
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView
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
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from settings.models import Settings
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import logging
from django.utils.timezone import make_aware

logger = logging.getLogger(__name__)

from decimal import Decimal
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views import View
from django.utils.timezone import now
import json
import logging
from django.shortcuts import get_object_or_404
from django.http import Http404






class ProductAutocompleteView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "")
        products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
        data = [{"id": product.id, "text": product.name, "price": str(product.unit_selling_price)} for product in products]
        print(data)
        return JsonResponse({"results": data})


    

from django.shortcuts import get_object_or_404
from django.core.serializers import serialize


from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
import json

class MakeSaleView(LoginRequiredMixin, TemplateView):
    template_name = "sales/makesale.html"
    
    def get(self, request, *args, **kwargs):
        context = {
            "products": Product.objects.all()
        }
        
        resume_id = request.GET.get('resume')
        if resume_id:
            try:
                paused_sale = get_object_or_404(Sale, id=resume_id)
                paused_items = paused_sale.saleproduct_set.select_related('product').all()

                # Custom serialization to include all fields and related data
                paused_items_serialized = json.dumps([
                    {
                        "id": item.id,
                        "product": {
                            "id": item.product.id,
                            "name": item.product.name,
                            "unit_selling_price": str(item.product.unit_selling_price),
                            "bulk_selling_price": str(item.product.bulk_selling_price),
                            "available_quantity": item.product.available_quantity,
                            "units_per_bulk": item.product.units_per_bulk,
                        },
                        "quantity": item.quantity,
                        "unit_cost_price": str(item.unit_cost_price),
                        "unit_selling_price": str(item.unit_selling_price),
                        "cost_price": str(item.cost_price),
                        "bulk_selling_price": str(item.bulk_selling_price),
                        "total": str(item.total),
                        "sale_type": item.sale_type,
                    }
                    for item in paused_items
                ], cls=DjangoJSONEncoder)

                context.update({
                    "resume_sale": paused_sale,
                    "paused_items": paused_items_serialized,
                    "sale_date": paused_sale.created_at.isoformat(),
                })
            except Exception as e:
                messages.error(request, f"Error: {e}")
        
        return render(request, self.template_name, context)



class PausedSalesListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = "sales/pausedsales.html"  # Template to render the sales list
    context_object_name = "paused_sales"  # Context variable name to access the sales in the template

    def get_queryset(self):
        # Filter sales with a status of 'Paused'
        return Sale.objects.filter(status='Paused').order_by('-created_at') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass SaleProduct data to the template
        context['sale_products'] = SaleProduct.objects.filter(sale__status='Paused')
        return context
    
    
    
class CompletedSalesListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = "sales/completedsales.html"  # Template to render the sales list
    context_object_name = "completed_sales"  # Context variable name to access the sales in the template

    def get_queryset(self):
        # Filter sales with a status of 'Paused'
        return Sale.objects.filter(status='Completed').order_by('-created_at') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass SaleProduct data to the template
        context['sale_products'] = SaleProduct.objects.filter(sale__status='Completed')
        return context


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
    Handles pausing a sale for later completion. Validates and stores sale data
    with 'Paused' status without reducing inventory or processing payment.
    """

    def validate_products_data(self, products_data):
        """Validate product details for sale."""
        if not isinstance(products_data, list):
            raise ValidationError("Products data must be a list")

        for item in products_data:
            required_fields = ['product_id', 'quantity', 'sale_type']
            missing_fields = [field for field in required_fields if field not in item]
            if missing_fields:
                raise ValidationError(f"Missing fields: {', '.join(missing_fields)}")

            if not str(item['product_id']).isdigit():
                raise ValidationError(f"Invalid product_id: {item['product_id']}")

            try:
                quantity = int(item['quantity'])
                if quantity <= 0:
                    raise ValidationError(f"Invalid quantity: {quantity}")
            except ValueError:
                raise ValidationError(f"Invalid quantity format: {item['quantity']}")

            if item['sale_type'] not in ['Unit', 'Bulk']:
                raise ValidationError(f"Invalid sale_type: {item['sale_type']}")

    def validate_sale_date(self, sale_date):
        """Validate and parse the sale date."""
        if sale_date:
            try:
                parsed_date = parse_datetime(sale_date)
                if parsed_date.tzinfo is None:
                    return make_aware(parsed_date)
                return parsed_date
            except (ValueError, TypeError):
                raise ValidationError(f"Invalid sale_date format: {sale_date}")
        return now()

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            # Parse input data
            data = json.loads(request.body)

            # Validate data
            self.validate_products_data(data.get('products', []))
            sale_date = self.validate_sale_date(data.get('sale_date'))

            # Initialize total amount and product details
            total_amount = Decimal('0.00')
            products_to_process = []

            for item in data['products']:
                product = Product.objects.get(id=item['product_id'])
                quantity = int(item['quantity'])

                # Determine price based on sale type
                if item['sale_type'] == 'Unit':
                    unit_cost_price = product.unit_cost_price
                    unit_selling_price = product.unit_selling_price
                    line_total = unit_selling_price * quantity
                else:  # Bulk
                    unit_cost_price = product.bulk_cost_price
                    unit_selling_price = product.bulk_selling_price
                    line_total = unit_selling_price * quantity

                # Accumulate total
                total_amount += line_total

                products_to_process.append({
                    'product': product,
                    'quantity': quantity,
                    'unit_cost_price': unit_cost_price,
                    'unit_selling_price': unit_selling_price,
                    'sale_type': item['sale_type'],
                    'line_total': line_total
                })

            # Create Sale instance
            sale = Sale.objects.create(
                created_at=sale_date,
                total_amount=total_amount,
                status='Paused',
                cashier_name=f"{request.user.first_name} {request.user.last_name}" if request.user.is_authenticated else None
            )
            
            sale.save()

            # Process sale products without updating inventory
            for product_info in products_to_process:
                SaleProduct.objects.create(
                    sale=sale,
                    product=product_info['product'],
                    quantity=product_info['quantity'],
                    unit_cost_price=product_info['unit_cost_price'],
                    unit_selling_price=product_info['unit_selling_price'],
                    sale_type=product_info['sale_type'],
                    total=product_info['line_total']
                )
                sale.calculate_total_profit()
                sale.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Sale paused successfully.',
                'sale_id': sale.id,
                'total_amount': str(total_amount)
            })

        except ValidationError as e:
            print(str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found.'}, status=404)

        except Exception as e:
            logger.error(f"Error pausing sale: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)
        
        
class DeleteSaleView(LoginRequiredMixin,DeleteView):
    model = Sale
    success_url = reverse_lazy("sales:pausedsales")
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Sale deleted succesfullly.")
        return super().delete(request, *args, **kwargs)
    
    


logger = logging.getLogger(__name__)

class CompleteSaleView(View):
    """
    Handles completing a sale, payment validation, and inventory updates.
    """

    def validate_payment_data(self, data):
        """Validate payment details."""
        payment_type = data.get('payment_type')
        amount_paid = data.get('amount_paid')

        # Validate payment type
        valid_payment_types = ['Cash', 'Mobile Money', 'Bank Transfer', 'Card']
        if not payment_type or payment_type not in valid_payment_types:
            raise ValidationError(f"Invalid payment type: {payment_type}")

        # Validate amount paid
        try:
            amount_paid = Decimal(str(amount_paid))
            if amount_paid < 0:
                raise ValidationError("Amount paid cannot be negative")
        except (TypeError, ValueError):
            raise ValidationError(f"Invalid amount paid: {amount_paid}")

        return payment_type, amount_paid

    def validate_products_data(self, products_data):
        """Validate product details for sale."""
        if not isinstance(products_data, list):
            raise ValidationError("Products data must be a list")

        for item in products_data:
            required_fields = ['product_id', 'quantity', 'sale_type']
            missing_fields = [field for field in required_fields if field not in item]
            if missing_fields:
                raise ValidationError(f"Missing fields: {', '.join(missing_fields)}")

            if not str(item['product_id']).isdigit():
                raise ValidationError(f"Invalid product_id: {item['product_id']}")

            try:
                quantity = int(item['quantity'])
                if quantity <= 0:
                    raise ValidationError(f"Invalid quantity: {quantity}")
            except ValueError:
                raise ValidationError(f"Invalid quantity format: {item['quantity']}")

            if item['sale_type'] not in ['Unit', 'Bulk']:
                raise ValidationError(f"Invalid sale_type: {item['sale_type']}")

    def validate_sale_date(self, sale_date):
        """Validate and parse the sale date."""
        if sale_date:
            try:
                parsed_date = parse_datetime(sale_date)
                if parsed_date.tzinfo is None:
                    return make_aware(parsed_date)
                return parsed_date
            except (ValueError, TypeError):
                raise ValidationError(f"Invalid sale_date format: {sale_date}")
        return now()

    def post(self, request, *args, **kwargs):
        try:
            # Parse input data
            data = json.loads(request.body)

            # Validate data
            self.validate_products_data(data.get('products', []))
            sale_date = self.validate_sale_date(data.get('sale_date'))
            payment_type, amount_paid = self.validate_payment_data(data)

            # Initialize total amount and product details
            total_amount = Decimal('0.00')
            products_to_process = []

            for item in data['products']:
                product = Product.objects.get(id=item['product_id'])
                quantity = int(item['quantity'])

                # Determine price based on sale type
                if item['sale_type'] == 'Unit':
                    unit_cost_price = product.unit_cost_price
                    unit_selling_price = product.unit_selling_price
                    line_total = unit_selling_price * quantity
                else:  # Bulk
                    unit_cost_price = product.bulk_cost_price
                    unit_selling_price = product.bulk_selling_price
                    line_total = unit_selling_price * quantity

                # Accumulate total
                total_amount += line_total

                products_to_process.append({
                    'product': product,
                    'quantity': quantity,
                    'unit_cost_price': unit_cost_price,
                    'unit_selling_price': unit_selling_price,
                    'sale_type': item['sale_type'],
                    'line_total': line_total
                })

            # Calculate balance
            balance = amount_paid - total_amount
            if balance < 0:
                raise ValidationError("Amount paid is less than the total amount due.")

            # Create Sale instance
            sale = Sale.objects.create(
                created_at=sale_date,
                total_amount=total_amount,
                status='Completed',
                payment_type=payment_type,
                amount_paid=amount_paid,
                balance=balance,
                cashier_name=f"{request.user.first_name} {request.user.last_name}" if request.user.is_authenticated else None
            )
            
            sale.save()

            # Process sale products and update inventory
            for product_info in products_to_process:
                SaleProduct.objects.create(
                    sale=sale,
                    product=product_info['product'],
                    quantity=product_info['quantity'],
                    unit_cost_price=product_info['unit_cost_price'],
                    unit_selling_price=product_info['unit_selling_price'],
                    sale_type=product_info['sale_type'],
                    total=product_info['line_total']
                )

                # Reduce inventory
                product_info['product'].available_quantity -= product_info['quantity']
                product_info['product'].save()
                sale.calculate_total_profit()
                sale.save()

            # Check receipt printing settings
            settings = Settings.objects.first()
            auto_print = settings.always_print_receipt if settings else False

            return JsonResponse({
                'status': 'success',
                'message': 'Sale completed successfully.',
                'sale_id': sale.id,
                'auto_print': auto_print
            })

        except ValidationError as e:
            print(str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found.'}, status=404)

        except Exception as e:
            logger.error(f"Error completing sale: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from django.http import HttpResponse

def generate_receipt(request, sale_id):
    # Get the sale and related products
    sale = Sale.objects.get(pk=sale_id)
    sale_products = sale.saleproduct_set.all().select_related('product')

    # Prepare sale data
    sale_data = {
        'store_name': 'VISAB ENTERPRISE',
        'store_address': 'Kakraba Junction Off the Nyanyano Road',
        'store_contact': 'Tel: 0242275752',
        'receipt_no': sale.sale_code,
        'date': sale.created_at.date(),
        'time': sale.created_at.time(),
        'cashier': sale.cashier_name,
        'products': [
            {
                'name': sp.product.name,
                'qty': str(sp.quantity),
                'type': sp.sale_type.lower(),
                'amount': float(sp.subtotal())
            }
            for sp in sale_products
        ],
        'total': float(sale.total_amount),
        'cash': float(sale.amount_paid),
        'cash_tendered': float(sale.amount_paid),
        'balance': float(sale.balance),
        'payment_type': sale.payment_type
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receipt_{sale_id}.pdf"'

    # Set up the PDF canvas
    c = canvas.Canvas(response, pagesize=(3 * inch, 11 * inch))  # Thermal receipt size
    y = 10.5 * inch  # Start from the top
    left_margin = 0.1 * inch  # Reduced left margin

    # Store header
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(1.5 * inch, y, sale_data['store_name'])
    y -= 0.2 * inch
    c.setFont("Helvetica", 8)
    c.drawCentredString(1.5 * inch, y, sale_data['store_address'])
    y -= 0.2 * inch
    c.drawCentredString(1.5 * inch, y, sale_data['store_contact'])
    y -= 0.3 * inch

    # Receipt info and cashier info
    # Receipt info and cashier info
    c.setFont("Helvetica", 8)
    c.drawString(left_margin, y, f"Receipt No: {sale_data['receipt_no']}")
    y -= 0.2 * inch
    c.drawString(left_margin, y, f"Date: {sale_data['date']}")
    y -= 0.2 * inch
    c.drawString(left_margin, y, f"Time: {sale_data['time']}")
    y -= 0.2 * inch
    c.drawString(left_margin, y, f"Cashier: {sale_data['cashier']}")
    y -= 0.3 * inch


    # Product header
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left_margin, y, "Item")
    c.drawString(left_margin + 1.0 * inch, y, "Qty")
    c.drawString(left_margin + 1.5 * inch, y, "Type")
    c.drawRightString(left_margin + 2.8 * inch, y, "Amount")
    y -= 0.2 * inch

    # Draw a line under the header
    c.line(left_margin, y, 2.9 * inch, y)
    y -= 0.1 * inch

    # Product details
    c.setFont("Helvetica", 8)
    for product in sale_data['products']:
        name = product['name'][:15] + "..." if len(product['name']) > 15 else product['name']
        c.drawString(left_margin, y, name)
        c.drawString(left_margin + 1.0 * inch, y, product['qty'])
        c.drawString(left_margin + 1.5 * inch, y, product['type'])
        c.drawRightString(left_margin + 2.8 * inch, y, f"{product['amount']:.2f}")
        y -= 0.2 * inch

        if y < 0.5 * inch:
            c.showPage()
            y = 10.5 * inch

    # Draw a line above totals
    y -= 0.1 * inch
    c.line(left_margin, y, 2.9 * inch, y)
    y -= 0.2 * inch

    # Total section
    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(left_margin + 2.8 * inch, y, f"Total: GHS {sale_data['total']:.2f}")
    y -= 0.3 * inch

    # Payment details
    c.setFont("Helvetica", 8)
    c.drawString(left_margin, y, f"Payment Type: {sale_data['payment_type']}")
    y -= 0.2 * inch
    c.drawString(left_margin, y, f"Amount Paid: GHS {sale_data['cash']:.2f}")
    y -= 0.2 * inch
    c.drawString(left_margin, y, f"Balance: GHS {sale_data['balance']:.2f}")
    y -= 0.3 * inch

    # Footer
    c.setFont("Helvetica", 7)
    c.drawCentredString(1.5 * inch, y, "Goods sold are not returnable.")
    y -= 0.2 * inch
    c.drawCentredString(1.5 * inch, y, "Thank You for Your Business!")
    y -= 0.2 * inch

    # Finalize and save
    c.showPage()
    c.save()

    return response