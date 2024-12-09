from django.urls import path

from .views import (
    ProductCategoryList,
    CreateProductCategoryView,
    EditProductCategoryView,
    DeleteProductCategoryView,
    DeleteAllProductCategoriesView,
    ProductListView,
    CreateProductView,
    EditProductView,
    DeleteProductView,
    PackageListView,
    CreateProductPackageView,
    EditProductPackageView,
    ExportProductCategoryExcelView,
    ExportProductCategoryPDFView,
    ExportProductPackageExcelView,
    ExportProductPackagePDFView,
    DeleteAllProductPackageView,
    ExportProductsExcelView,
    ExportProductPDFView,
    DeleteAllProductView,
    ResetProductQuantityView
)
app_name='product'


urlpatterns=[
    path('categories/', ProductCategoryList.as_view(), name='categorylist'),
    path("category/add/",CreateProductCategoryView.as_view(),name="addcategory"),
    path('category/edit/<int:pk>/', EditProductCategoryView.as_view(), name='editcategory'),
    path('category/delete/<int:pk>/', DeleteProductCategoryView.as_view(), name='deletecategory'),
    path('category/delete-all/', DeleteAllProductCategoriesView.as_view(), name='deleteallcategories'),
    path('list/', ProductListView.as_view(), name='productlist'),
    path('add/', CreateProductView.as_view(), name='addproduct'),
    path('edit/<int:pk>/', EditProductView.as_view(), name='editproduct'),
    path('delete-all/', DeleteAllProductView.as_view(), name='delete-all'),
    path('reset-all/', ResetProductQuantityView.as_view(), name='reset-all'),
    path('delete/<int:pk>/', DeleteProductView.as_view(), name='deleteproduct'),
    path('package/list/', PackageListView.as_view(), name='packagelist'),
    path('package/add/', CreateProductPackageView.as_view(), name='addpackage'),
    path('package/edit/<int:pk>/', EditProductPackageView.as_view(), name='editpackage'),
    path('package/delete-all/', DeleteAllProductPackageView.as_view(), name='deleteallpackage'),
    path('categories/export-excel/', ExportProductCategoryExcelView.as_view(), name='exportexcel'),
    path('categories/export-pdf/', ExportProductCategoryPDFView.as_view(), name='exportpdf'),
    path('package/export-excel/', ExportProductPackageExcelView.as_view(), name='exportpackageexcel'),
    path('package/export-pdf/', ExportProductPackagePDFView.as_view(), name='exportpackagepdf'),
    path('export-pdf/', ExportProductPDFView.as_view(), name='exportproductpdf'),
    path('export-excel/', ExportProductsExcelView.as_view(), name='exportproductexcel'),











 

]