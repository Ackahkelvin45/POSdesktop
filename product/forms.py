from django import forms
from .models import ProductCategory,Product,ProductPackage


class ProductCategoryForm(forms.ModelForm):

    class Meta:
        model = ProductCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 2:
            raise forms.ValidationError("Category name must be at least 2 characters long.")
        if self.instance.pk: 
            if ProductCategory.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("A category with this name already exists.")
        else:
            if ProductCategory.objects.filter(name=name).exists():
                raise forms.ValidationError("A category with this name already exists.")
        return name

    def save(self, commit=True):
        category = super().save(commit=False)
        if commit:
            category.save()
        return category


class ProductCreationForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select  select2  form-control-lg','id':"product_id"}),
        empty_label="Select a product category",
        required=True
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'unit_selling_price',"unit_cost_price","bulk_selling_price",'bulk_cost_price', 'category', 'available_quantity', 'image','units_per_bulk']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'available_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': 1, 'min': 0}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'unit_selling_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0',"step":"0.01"}),
            'unit_cost_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0',"step":"0.01"}),
            'bulk_selling_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0',"step":"0.01"}),
            'bulk_cost_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0',"step":"0.01"}),
            'units_per_bulk': forms.NumberInput(attrs={'class': 'form-control', 'min': '0',"step":"1"}),

            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'multiple': False,
                'data-allow-reorder': 'true',
                'data-max-file-size': '3MB',
                'data-max-files': '1',
                "name":"image" ,
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if self.instance.pk:  
            if Product.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("A product with this name already exists.")
        else:
            if Product.objects.filter(name=name).exists():
                raise forms.ValidationError("A product with this name already exists.")
        return name

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price must be a positive number.")
        return price

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("Quantity must be a positive number.")
        return quantity

    def save(self, commit=True):
        product = super().save(commit=False)
        if commit:
            product.save()
        return product





class ProductPackageForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select select2  form-control-lg','id':"product_id"}),
        empty_label="Select a product",
        required=True
    )

    class Meta:
        model = ProductPackage
        fields = ['name', 'description', 'product', 'package_price', 'quantity', 'product_quantity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'package_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.01}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'product_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if self.instance.pk:  
            if ProductPackage.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("A package with this name already exists.")
        else:
            if ProductPackage.objects.filter(name=name).exists():
                raise forms.ValidationError("A package with this name already exists.")
        return name

    def clean_package_price(self):
        package_price = self.cleaned_data.get('package_price')
        if package_price is not None and package_price < 0:
            raise forms.ValidationError("Package price must be a positive number.")
        return package_price

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("Total quantity of the package must be a positive number.")
        return quantity

    def clean_product_quantity(self):
        product_quantity = self.cleaned_data.get('product_quantity')
        if product_quantity is not None and product_quantity < 0:
            raise forms.ValidationError("Product quantity in the package must be a positive number.")
        return product_quantity

    def save(self, commit=True):
        package = super().save(commit=False)
        if commit:
            package.save()
        return package