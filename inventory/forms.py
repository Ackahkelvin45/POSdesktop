from django import forms
from .models import InventoryLog
from product.models import Product


class InventoryLogForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select select2  form-control-lg','id':"product_id"}),
        empty_label="Select a product",
        required=True
    )
    class Meta:
        model = InventoryLog
        fields = [
            'product',
            'action',
            'quantity',
            'notes',
        ]
        widgets = {
            
            'action': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity'}),

            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter additional notes (optional)'}),
        }
        help_texts = {
            'quantity': 'Specify the number of units for this action.',
            'notes': 'Provide any extra details or comments about this action.',
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity
