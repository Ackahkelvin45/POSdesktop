from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
def showDasboard(request):
    return render(request, 'dashboard/dashboard.html')


class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = 'dashboard/dashboard.html'
   
    