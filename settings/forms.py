from django import forms
from .models import Settings

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['always_print_receipt', 'change_date_sale']
        labels = {
            'change_date': 'Enable Date Change',
            'always_print_receipt': 'Always Print Receipt',
            'change_date_sale': 'Enable Sale Date Change'
        }
        widgets = {
            'always_print_receipt': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'change_date_sale': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
