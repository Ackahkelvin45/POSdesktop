from django.shortcuts import render
from .forms import  UserCreationForm,EditUserForm
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView,DeleteView
from authentication.models import CustomUser
from django.contrib.auth import get_user_model
from django.views.generic.edit import DeleteView



class UserListView(ListView):
    model=CustomUser
    template_name="users/userlist.html"
    context_object_name="users"

class CreateUserView(FormView):
    template_name = 'users/adduser.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('users:userslist')  # Replace 'success_url' with your actual URL name

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.capitalize()}: {error}")
        
        return super().form_invalid(form)

class EditUserView(UpdateView):
    model = get_user_model()
    form_class = EditUserForm  # The form for editing user data
    template_name = 'users/edituser.html'  # Template to render the form
    success_url = reverse_lazy('users:userslist')  # Redirect after success
    context_object_name = "user"

    def get_object(self, queryset=None):
        user = super().get_object(queryset=queryset)
        return user
    def form_valid(self, form):
        # Call the superclass to save the object
        user = form.save(commit=False)

        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        # Handle form errors and add them to messages
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.capitalize()}: {error}")
        return super().form_invalid(form)
    
  


    

class DeleteUserView(DeleteView):
    model = CustomUser
    success_url = reverse_lazy('users:userslist')  
    
    def delete(self, request, *args, **kwargs):
        # Optional: Add a custom message before deletion
        messages.success(self.request, f"User {self.get_object().email} has been deleted successfully.")
        return super().delete(request, *args, **kwargs)