from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Settings
from .forms import SettingsForm
from django.views import View
from django.http import JsonResponse

def edit_settings(request):
    # Get the first settings object or create if it doesn't exist
    settings_obj, created = Settings.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('settings:edit_settings')
    else:
        form = SettingsForm(instance=settings_obj)
    
    return render(request, 'settings/edit_settings.html', {'form': form})



class GetSettingsView(View):
    def get(self, request):
        settings = Settings.objects.first()
        if settings:
            return JsonResponse({
                'change_date_sale': settings.change_date_sale,
                'always_print_receipt': settings.always_print_receipt
            })
        return JsonResponse({
            'change_date_sale': False,
            'always_print_receipt': False
        })
        
        
        
        
