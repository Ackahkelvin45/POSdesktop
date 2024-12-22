from django.shortcuts import render
from django.views.generic.list import ListView
from .models import GlobalActivityLog
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

class GlobalActivityLogListView(LoginRequiredMixin,ListView):
    model = GlobalActivityLog
    template_name = 'activities/activities.html'
    context_object_name = 'logs'
    ordering = ['-timestamp']