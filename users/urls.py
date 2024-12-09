from django.urls import path 
from .views import CreateUserView,UserListView,EditUserView,DeleteUserView

app_name="users"

urlpatterns = [
   path("add/",CreateUserView.as_view(),name="usersadd"),
   path("list/",UserListView.as_view(),name="userslist") ,  
   path("edit/<int:pk>",EditUserView.as_view(),name="editusers") ,  
    path("delete/<int:pk>",DeleteUserView.as_view(),name="deleteusers") ,  
]