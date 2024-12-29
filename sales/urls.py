from django.urls import path
from  .views import MakeSaleView,ProductAutocompleteView,ProductFilterView,PauseSaleView,PausedSalesListView,DeleteSaleView,CompleteSaleView,CompletedSalesListView
from . import views

app_name="sales"

urlpatterns =[
    path ("new/",MakeSaleView.as_view(),name="addsale"),
    path("product-autocomplete/", ProductAutocompleteView.as_view(), name="product_autocomplete"),
    path('products/filter/', ProductFilterView.as_view(), name='product-filter'),
    path('pause/', PauseSaleView.as_view(), name='pause-sale'),
    path('paused/all', PausedSalesListView.as_view(), name='pausedsales'),
    path('completed/all', CompletedSalesListView.as_view(), name='completedsales'),

    path('paused/delete/<int:pk>', DeleteSaleView.as_view(), name='deletesale'),
    path('complete/', CompleteSaleView.as_view(), name='completesale'),
    path('receipt/<int:sale_id>/', views.generate_receipt, name='generate_receipt'),

]