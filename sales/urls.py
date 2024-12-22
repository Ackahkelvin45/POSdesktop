from django.urls import path
from  .views import MakeSaleView,ProductAutocompleteView,ProductFilterView


app_name="sales"

urlpatterns =[
    path ("new/",MakeSaleView.as_view(),name="addsale"),
    path("product-autocomplete/", ProductAutocompleteView.as_view(), name="product_autocomplete"),
    path('products/filter/', ProductFilterView.as_view(), name='product-filter'),


]