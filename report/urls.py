from django.urls import path 
from . import views 
app_name="report"


urlpatterns = [
    path('analytics/', views.inventory_charts, name='analytics'),
    path('sales-report/', views.SalesReport.as_view(), name='sales_summary_page'),

    path('sales-data/', views.get_sales_data, name='sales-data'),

]