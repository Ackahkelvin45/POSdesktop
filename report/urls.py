from django.urls import path 
from . import views 
app_name="report"


urlpatterns = [
    path('inventory-analytics/', views.inventory_charts, name='analytics'),
    path('sales-analytics/', views.SalesReport.as_view(), name='sales_summary_page'),
path('sales-report/', views.product_report, name='product_report'),
    path('sales-data/', views.get_sales_data, name='sales-data'),
    path('export-report-csv/', views.export_report_csv, name='export_report_csv'),
    path('export-report-pdf/', views.ExportReportPDFView.as_view(), name='export_report_pdf'),

]