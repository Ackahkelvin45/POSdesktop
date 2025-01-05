from django.shortcuts import render
from django.db.models import Sum, F
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.views import View
from sales.models import Sale, SaleProduct
from product.models import Product,ProductCategory
from collections import defaultdict
from inventory.models import InventoryLog
from datetime import timedelta
from django.utils.timezone import now
from django.views.generic.base import TemplateView

def inventory_charts(request):
    # Get the stock levels for products
    stock_levels = Product.objects.all()

    # Get the number of products in stock, low stock, and out of stock
    stock_status = {
        "in_stock": Product.objects.filter(available_quantity__gt=10).count(),
        "low_stock": Product.objects.filter(available_quantity__lte=10, available_quantity__gt=0).count(),
        "out_of_stock": Product.objects.filter(available_quantity=0).count(),
    }

    # Prepare data for the stock pie chart
    data = Product.objects.values('name', 'available_quantity')
    labels = [item['name'] for item in data]
    quantities = [item['available_quantity'] for item in data]

    # Prepare data for the category pie chart
    category_data = ProductCategory.objects.annotate(product_count=Count('products'))
    category_labels = [item.name for item in category_data]
    category_counts = [item.product_count for item in category_data]

    return render(request, 'report/analytics.html', {
        'stock_levels': stock_levels,
        'stock_status': stock_status,
        'labels': labels,
        'quantities': quantities,
        'category_labels': category_labels,
        'category_counts': category_counts,
    })



class SalesReport(TemplateView):
    template_name ='report/sales.html'
 



from django.http import JsonResponse
from django.db.models import Sum, F, Count
from django.utils.timezone import now, timedelta
from django.http import JsonResponse
from django.db.models import F, Sum, Count, DateField, Func
from django.utils.timezone import now, timedelta

from django.db.models import F, Sum, Count, Func
from django.utils.timezone import now, timedelta
from django.http import JsonResponse


from django.http import JsonResponse
from django.db.models import Sum, Count, Func, F
from django.db.models.functions import TruncDate
from django.utils.timezone import now, timedelta



from django.http import JsonResponse
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils.timezone import now, timedelta

def get_sales_data(request):
    filter_type = request.GET.get('filter', 'day')  # Default to 'day'
    today = now()

    # Determine start and previous period dates
    if filter_type == 'day':
        start_date = today - timedelta(days=1)
        prev_start_date = today - timedelta(days=2)
        prev_end_date = today - timedelta(days=1)
        trunc_period = TruncDate('created_at')
    elif filter_type == 'week':
        start_date = today - timedelta(weeks=1)
        prev_start_date = today - timedelta(weeks=2)
        prev_end_date = today - timedelta(weeks=1)
        trunc_period = TruncWeek('created_at')  # Use TruncWeek for SQLite compatibility
    elif filter_type == 'month':
        start_date = today - timedelta(days=30)
        prev_start_date = today - timedelta(days=60)
        prev_end_date = today - timedelta(days=30)
        trunc_period = TruncMonth('created_at')  # Use TruncMonth for SQLite compatibility
    else:
        return JsonResponse({'error': 'Invalid filter type'}, status=400)

    # Current period data
    current_data = Sale.objects.filter(created_at__gte=start_date,status="Completed").aggregate(
        total_sales=Sum('total_amount') or 0,
        total_profit=Sum('total_profit') or 0,
        total_sales_count=Count('id')
    )

    # Previous period data
    previous_data = Sale.objects.filter(
        created_at__gte=prev_start_date, created_at__lt=prev_end_date,status="Completed"
    ).aggregate(
        total_sales=Sum('total_amount') or 0,
        total_profit=Sum('total_profit') or 0,
        total_sales_count=Count('id')
    )

    # Calculate percentage change
    def calculate_change(current, previous):
        if previous == 0:  # Avoid division by zero
            return "Stable" if current == 0 else "100% Increase"
        change = ((current - previous) / previous) * 100
        return f"{change:.2f}% {'Increase' if change > 0 else 'Decrease'}"

    sales_change = calculate_change(current_data['total_sales'] or 0, previous_data['total_sales'] or 0)
    profit_change = calculate_change(current_data['total_profit'] or 0, previous_data['total_profit'] or 0)
    sales_count_change = calculate_change(current_data['total_sales_count'] or 0, previous_data['total_sales_count'] or 0)

    # Get individual sales data
    sales_data = (
        Sale.objects.filter(created_at__gte=start_date,status="Completed")
        .order_by('created_at')  # Order by creation time
        .values('id', 'total_amount', 'total_profit')  # Get only needed fields
    )

    # Format data for Chart.js
    chart_data = {
        'labels': [sale['id'] for sale in sales_data],  # Use IDs as labels
        'sales': [sale['total_amount'] for sale in sales_data],
        'profits': [sale['total_profit'] for sale in sales_data],
        'total_sales': current_data['total_sales'] or 0,
        'total_profit': current_data['total_profit'] or 0,
        'total_sales_count': current_data['total_sales_count'] or 0,
        'sales_change': sales_change,
        'profit_change': profit_change,
        'sales_count_change': sales_count_change,
    }
    return JsonResponse(chart_data)



# views.py
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from product.models import Product
from sales.models import Sale, SaleProduct
from inventory.models import InventoryLog
   
   
   
def product_report(request):
    # Get date parameters from request, or use default 24-hour range
    end_date = request.GET.get('end_date')
    start_date = request.GET.get('start_date')
    
    # If no dates provided, set default 24-hour range
    if not end_date:
        end_date = timezone.now()
        end_date_str = end_date.strftime('%Y-%m-%d')
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        end_date_str = end_date.strftime('%Y-%m-%d')
    
    if not start_date:
        start_date = end_date - timedelta(days=1)
        start_date_str = start_date.strftime('%Y-%m-%d')
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        start_date_str = start_date.strftime('%Y-%m-%d')
    
    report_data = []
    
    # Get all products
    products = Product.objects.all()
    
    for product in products:
        # Get total quantity sold in date range
        sales = SaleProduct.objects.filter(
            sale__created_at__range=(start_date, end_date),
            product=product
        ).aggregate(total_sold=Sum('quantity'))['total_sold'] or 0
        
        # Get total inventory added in date range
        inventory_added = InventoryLog.objects.filter(
            product=product,
            action='add',
            action_date__range=(start_date, end_date)
        ).aggregate(total_added=Sum('quantity'))['total_added'] or 0
        
        # Calculate starting quantity
        starting_quantity = product.available_quantity - inventory_added + sales
        
        report_data.append({
            'product_name': product.name,
            'starting_quantity': starting_quantity,
            'inventory_added': inventory_added,
            'quantity_sold': sales,
            'current_quantity': product.available_quantity,
            'matches': (starting_quantity + inventory_added - sales) == product.available_quantity
        })
    
    context = {
        'report_data': report_data,
        'start_date': start_date_str,
        'end_date': end_date_str
    }
    
    return render(request, 'report/product_report.html', context)




from django.http import HttpResponse

import csv


def export_report_csv(request):
    # Get the same date range parameters as the main report
    end_date = request.GET.get('end_date')
    start_date = request.GET.get('start_date')
    
    if not end_date:
        end_date = timezone.now()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    
    if not start_date:
        start_date = end_date - timedelta(days=1)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="report_{start_date.strftime("%Y%m%d")}-{end_date.strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Product Name', 'Starting Quantity', 'Inventory Added', 'Quantity Sold', 'Current Quantity'])

    products = Product.objects.all()
    
    for product in products:
        sales = SaleProduct.objects.filter(
            sale__created_at__range=(start_date, end_date),
            product=product
        ).aggregate(total_sold=Sum('quantity'))['total_sold'] or 0
        
        inventory_added = InventoryLog.objects.filter(
            product=product,
            action='add',
            action_date__range=(start_date, end_date)
        ).aggregate(total_added=Sum('quantity'))['total_added'] or 0
        
        starting_quantity = product.available_quantity - inventory_added + sales
        
        writer.writerow([
            product.name,
            starting_quantity,
            inventory_added,
            sales,
            product.available_quantity
        ])

    return response





from django.views import View
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
import pandas as pd
from django.utils import timezone

class ExportReportPDFView(View):
    def get(self, request, *args, **kwargs):
        # Get the date range parameters
        end_date = request.GET.get('end_date')
        start_date = request.GET.get('start_date')
        
        if not end_date:
            end_date = timezone.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        
        if not start_date:
            start_date = end_date - timedelta(days=1)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        # Prepare report data
        report_data = []
        products = Product.objects.all()
        
        for product in products:
            sales = SaleProduct.objects.filter(
                sale__created_at__range=(start_date, end_date),
                product=product
            ).aggregate(total_sold=Sum('quantity'))['total_sold'] or 0
            
            inventory_added = InventoryLog.objects.filter(
                product=product,
                action='add',
                action_date__range=(start_date, end_date)
            ).aggregate(total_added=Sum('quantity'))['total_added'] or 0
            
            starting_quantity = product.available_quantity - inventory_added + sales
            
            report_data.append({
                'product_name': product.name,
                'starting_quantity': starting_quantity,
                'inventory_added': inventory_added,
                'quantity_sold': sales,
                'current_quantity': product.available_quantity,
                'matches': (starting_quantity + inventory_added - sales) == product.available_quantity
            })

        # Convert to DataFrame for easier handling
        df = pd.DataFrame(report_data)
        data = df.to_dict(orient="records")
        
        # Prepare context for template
        context = {
            'report_data': data,
            'company_name': "Your Company Name",  # Customize this
            'logo_url': "path/to/your/logo.png",  # Customize this
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'now': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        # Render the template
        template = get_template('report/report_pdf.html')
        html = template.render(context)

        # Generate PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{start_date.strftime("%Y%m%d")}-{end_date.strftime("%Y%m%d")}.pdf"'

        # Create PDF
        pisa_status = pisa.CreatePDF(html, dest=response)
        
        # Return error response if PDF generation failed
        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500)
        
        return response