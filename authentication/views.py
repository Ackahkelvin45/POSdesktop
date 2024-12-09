from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.shortcuts import redirect
from .forms import LoginForm 
from django.contrib import messages  




#Login View for User
class LoginView(FormView):
    template_name = 'auth/login.html'  
    form_class = LoginForm
    success_url = reverse_lazy('dashboard:dashboardpage') 
    def form_valid(self, form):
        user = form.get_user()
        if user is not None:
            login(self.request, user)
            next_url = self.request.GET.get('next', self.success_url)
            return redirect(next_url)
        return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Invalid email or password.") 
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

# LogoutView User.
class LogoutView(LogoutView):
    next_page = reverse_lazy('auth:login')
    
    
    
