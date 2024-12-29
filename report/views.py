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