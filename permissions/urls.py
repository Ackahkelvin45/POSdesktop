from django.urls import path

from .views import GroupsAndPermissionsView, EditGroupPermissionsView,DeleteGroupView,AddGroupView
app_name = 'permissions'

urlpatterns = [
  path('groups/', GroupsAndPermissionsView.as_view(), name='groups_permissions'), 
   path('edit-permissions/<int:pk>/', EditGroupPermissionsView.as_view(), name='edit_group_permissions'),
     path('delete/<int:pk>/', DeleteGroupView.as_view(), name='delete_group'),
      path('add/', AddGroupView.as_view(), name='add_group'),
]


from django.urls import path


