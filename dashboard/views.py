from django.db.models import Sum
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.views.generic import TemplateView
from sales.models import Sale, SaleProduct
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F

from django.utils import timezone
from datetime import timedelta


from datetime import timedelta
from django.utils import timezone
from django.db.models import F, Sum

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate the time 24 hours ago from now
        last_24_hours = timezone.now() - timedelta(hours=24)

        # Calculate the time 7 days ago from now
        last_7_days = timezone.now() - timedelta(days=7)

        # Query to get the top 10 selling products by total quantity sold
        top_selling_products = SaleProduct.objects.values('product__name', 'product_id') \
            .annotate(total_quantity_sold=Sum('quantity')) \
            .order_by('-total_quantity_sold')[:10]

        # Add the top selling products to the context
        context['top_selling_products'] = top_selling_products
        print(top_selling_products)

        # Query to get the sales made in the past 24 hours, grouped by sale_id
        daily_sales_trend = Sale.objects.filter(created_at__gte=last_24_hours,status="Completed") \
            .annotate(sale_id=F('id')) \
            .values('sale_id', 'total_amount') \
            .order_by('sale_id')

        # Add the daily sales trend to the context
        context['daily_sales_trend'] = daily_sales_trend

        # Query to get the sales made in the past 7 days, grouped by sale_id
        weekly_sales_trend = Sale.objects.filter(created_at__gte=last_7_days,status="Completed") \
            .annotate(sale_id=F('id')) \
            .values('sale_id', 'total_amount') \
            .order_by('sale_id')

        # Add the weekly sales trend to the context
        context['weekly_sales_trend'] = weekly_sales_trend

        return context
