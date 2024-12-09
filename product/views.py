from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView,DeleteView
from .forms import ProductCategoryForm,ProductCreationForm,ProductPackageForm
from .models import ProductCategory,Product,ProductPackage
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import redirect
import pandas as pd
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils import timezone



# Create your views here.


class ProductCategoryList(ListView):
    model = ProductCategory
    template_name = 'products/categorylist.html'
    context_object_name = 'categories'
    
    

class CreateProductCategoryView(FormView):
    template_name = "products/addcategory.html"
    form_class = ProductCategoryForm
    success_url = reverse_lazy("product:categorylist")
    
    def get_success_url(self):
      
        next_url = self.request.GET.get('next')
        print(next_url)
        if next_url:
            return next_url
        return super().get_success_url()

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.capitalize()}: {error}")
        return super().form_invalid(form)



class EditProductCategoryView(UpdateView):
    model = ProductCategory
    template_name = "products/editcategory.html"
    form_class = ProductCategoryForm
    context_object_name = "category"
    success_url = reverse_lazy("product:categorylist")  # Make sure this URL name exists

    def form_valid(self, form):
        messages.success(self.request, "Category updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.capitalize()}: {error}")
        return super().form_invalid(form)



class DeleteProductCategoryView(DeleteView):
    model = ProductCategory
    success_url = reverse_lazy("product:categorylist")
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Category deleted successfully.")
        return super().delete(request, *args, **kwargs)
    
    
class DeleteAllProductCategoriesView(View):
    def get(self, request, *args, **kwargs):
        # Delete all ProductCategories
        ProductCategory.objects.all().delete()
        
        messages.success(request, "All categories have been deleted successfully.")
        return redirect('product:categorylist')
    
    



class CreateProductView(FormView):
    template_name="products/addproduct.html"
    form_class=ProductCreationForm
    success_url=reverse_lazy("product:productlist")
    
    def form_valid(self, form) :
        form.save()
        return super().form_valid(form)
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.capitalize()}: {error}")
        
        return super().form_invalid(form)



class ProductListView(ListView):
    model = Product
    template_name = 'products/productlist.html'
    context_object_name = 'products'






class EditProductView(UpdateView):
    model = Product
    template_name = "products/editproduct.html"
    form_class = ProductCreationForm
    context_object_name = "product"
    success_url = reverse_lazy("product:productlist")  # Make sure this URL name exists

    def form_valid(self, form):
        messages.success(self.request, "Product updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.capitalize()}: {error}")
        return super().form_invalid(form)


class DeleteProductView(DeleteView):
    model = Product
    success_url = reverse_lazy("product:productlist")
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "product deleted successfully.")
        return super().delete(request, *args, **kwargs)
    
class DeleteAllProductView(View):
    def get(self, request, *args, **kwargs):
        # Delete all ProductCategories
        Product.objects.all().delete()
        
        messages.success(request, "All products have been deleted successfully.")
        return redirect('product:productlist') 
    
class PackageListView(ListView):
    model = ProductPackage
    template_name = 'products/packagelist.html'
    context_object_name = 'packages'


class CreateProductPackageView(FormView):
    form_class=ProductPackageForm
    template_name="products/addpackage.html"
    success_url = reverse_lazy('product:packagelist')
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Package Created successfully.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.capitalize()}: {error}")
        return super().form_invalid(form)


class EditProductPackageView(UpdateView):
    model = ProductPackage
    template_name = "products/editpackage.html"
    form_class = ProductPackageForm
    context_object_name = "package"
    success_url = reverse_lazy("product:packagelist")  # Make sure this URL name exists

    def form_valid(self, form):
        messages.success(self.request, "Package updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.capitalize()}: {error}")
        return super().form_invalid(form)
    
    
    
    
class ExportProductCategoryExcelView(View):
    def get(self, request, *args, **kwargs):
        categories = ProductCategory.objects.all()
        data = [
            {"ID": category.id, "Name": category.name, "Description": category.description}
            for category in categories
        ]

        df = pd.DataFrame(data)

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="product_categories.xlsx"'

        with pd.ExcelWriter(response, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Categories")

        return response
    
    
    
class ExportProductCategoryPDFView(View):
    def get(self, request, *args, **kwargs):
        # Fetch data from the database
        categories = ProductCategory.objects.values("id", "name", "description")

        # Convert to DataFrame
        df = pd.DataFrame(categories)

        data = df.to_dict(orient="records")
        current_time = timezone.now()

        # Render the template
        template = get_template("products/categoriespdf.html")
        context = {
            "categories": data,
            "company_name": "Your Company Name",
            "logo_url": "https://example.com/your-logo.png",
            "now": current_time.strftime('%Y-%m-%d %H:%M:%S'), 
        }
        html = template.render(context)

        # Generate PDF
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="categories.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse("Error generating PDF", status=500)

        return response


    
class ExportProductPackageExcelView(View):
    def get(self, request, *args, **kwargs):
        packages = ProductPackage.objects.all()
        data = [
            {"ID": package.id,"Name": package.name,"Product":package.product.name, "Number of Products":package.product_quantity,  "Price":package.package_price,"Description": package.description}
            for package in packages
        ]

        df = pd.DataFrame(data)

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="product_packages.xlsx"'

        with pd.ExcelWriter(response, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Packages")

        return response
    
    



class ExportProductPackagePDFView(View):
    def get(self, request, *args, **kwargs):
        product_packages = ProductPackage.objects.select_related("product").all()  

        data = []
        for package in product_packages:
            data.append({
                "name": package.name,
                "product_name": package.product.name,
                "product_quantity": package.product_quantity,
                "available_quantity": package.available_quantity,
                "description": package.description,
            })

        # Get the current time
        current_time = timezone.now()

        # Render the template
        template = get_template("products/packagepdf.html")
        context = {
            "product_packages": data,
            "company_name": "Your Company Name",
            "logo_url": "https://example.com/your-logo.png",
            "now": current_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        html = template.render(context)

        # Generate PDF
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="product_packages.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse("Error generating PDF", status=500)

        return response
    
    
class DeleteAllProductPackageView(View):
    def get(self, request, *args, **kwargs):
        # Delete all ProductCategories
        ProductPackage.objects.all().delete()
        
        messages.success(request, "All packages have been deleted successfully.")
        return redirect('product:packagelist') 
    
    
    
    
class ExportProductsExcelView(View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        data = [
            {"ID": product.id,"Name": product.name,"Category":product.category.name, "Available Quantity":product.available_quantity,  "Unit Cost Price":product.unit_cost_price,"Unit Selling Price":product.unit_selling_price,'Bulk Cost Price':product.bulk_cost_price,'Bulk Selling Pricce':product.bulk_selling_price,"Description": product.description}
            for product in products
        ]

        df = pd.DataFrame(data)

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="Products.xlsx"'

        with pd.ExcelWriter(response, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Products")

        return response
    
    
class ExportProductPDFView(View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.select_related("category").all()  

        data = []
        for product in products:
            data.append({
                "name": product.name,
                "category": product.category.name,
                "product_quantity": product.available_quantity,
                "unit_cost_price": product.unit_cost_price,
                "unit_selling_price": product.unit_selling_price,
                "bulk_cost_price": product.bulk_cost_price,
               "bulk_selling_price": product.bulk_selling_price,
                "description": product.description,
            })

        # Get the current time
        current_time = timezone.now()

        # Render the template
        template = get_template("products/productspdf.html")
        context = {
            "products": data,
            "company_name": "Your Company Name",
            "logo_url": "https://example.com/your-logo.png",
            "now": current_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        html = template.render(context)

        # Generate PDF
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="products.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse("Error generating PDF", status=500)

        return response
    
    
class DeleteAllProductView(View):
    def get(self, request, *args, **kwargs):
        # Delete all ProductCategories
        Product.objects.all().delete()
        
        messages.success(request, "All product have been deleted successfully.")
        return redirect('product:productlist')
    
class ResetProductQuantityView(View):
    def get(self, request, *args, **kwargs):
            # Reset available_quantity for all products to zero
            Product.objects.update(available_quantity=0)
            messages.success(request, "All product available_quantity have been set to zero.")
            return redirect('product:productlist') 

    
    
