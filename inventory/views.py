from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic.edit import FormView,UpdateView
from django.views.generic.list import ListView
from .forms import InventoryLogForm
from .models import InventoryLog
from django.http import JsonResponse
from product.models import Product
from django.views.generic.base import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse


class CreateInventoryLogView(FormView):
    template_name = "inventory/addinventory.html"
    form_class = InventoryLogForm
    success_url = reverse_lazy("inventory:inventorylist")  # Adjust to your URL name for the inventory log list

    def form_valid(self, form):
        # Save the form and create the inventory log
        form.save()
        messages.success(self.request, "Inventory log created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Add error messages to be displayed in the template
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.capitalize()}: {error}")
        return super().form_invalid(form)


from django.views.generic.list import ListView

class IventoryLogListView(ListView):
    model = InventoryLog
    template_name = 'inventory/invemtorylist.html'
    context_object_name = 'inventory'
    ordering = ['-id']  # Ensure logs are ordered by most recent first

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the most recent log
        context['most_recent_log'] = self.get_queryset().first()
        return context





class ProductQuantityView(View):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            return JsonResponse({'success': True, 'quantity': product.available_quantity})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'})


class EditInventoryLogView(UpdateView):
    model = InventoryLog
    template_name = "inventory/editinventorylog.html"
    form_class = InventoryLogForm
    success_url = reverse_lazy("inventory:inventorylist")  # Adjust to the URL name for your inventory log list
    context_object_name = "inventorylog"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_log = self.get_object()
        context['current_quantity'] = inventory_log.product.available_quantity
        return context
    def form_valid(self, form):
        # Save the updated inventory log
        form.save()
        messages.success(self.request, "Inventory log updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Add error messages to be displayed in the template
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.capitalize()}: {error}")
        return super().form_invalid(form)
    
    
    
    

class UndoInventoryLogView(View):
    def post(self, request, *args, **kwargs):
        # Get the inventory log by ID
        log_id = self.kwargs.get('pk')
        log = get_object_or_404(InventoryLog, id=log_id)

        # Check if it is the most recent log for this product
        most_recent_log = InventoryLog.objects.filter(product=log.product).order_by('-action_date').first()
        if log != most_recent_log:
            messages.error(request, "Only the most recent log can be undone.")
            return redirect(reverse_lazy('inventory:inventorylist'))

        # Perform the reverse action
        try:
            log.reverse_action()
            messages.success(request,f"Inventory action successfully reversed.")
        except Exception as e:
            messages.error(request, f"Error reversing inventory action: {str(e)}")

        return redirect(reverse('inventory:inventorylist'))
