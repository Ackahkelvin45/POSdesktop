from django.shortcuts import render
from django.views.generic.list import ListView
from .models import GlobalActivityLog
# Create your views here.

class GlobalActivityLogListView(ListView):
    model = GlobalActivityLog
    template_name = 'activities/activities.html'
    context_object_name = 'logs'
    ordering = ['-timestamp']