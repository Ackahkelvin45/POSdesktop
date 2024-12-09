from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.shortcuts import redirect
from django.contrib import messages
from authentication.models import CustomUser
from django.urls import reverse_lazy

class GroupsAndPermissionsView(TemplateView):
    template_name = "permissions/viewpermissions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        groups = Group.objects.prefetch_related('permissions') 
        groups_data = []

        for group in groups:
            permissions = group.permissions.all()
            groups_data.append({
                'group': group.name,
                'id':group.id,
                'permissions': permissions,
                'has_permissions': permissions.exists(),
            })

        context['groups'] = groups_data
        return context
    
 



class EditGroupPermissionsView(TemplateView):
    template_name = 'permissions/editpermissions.html'

    def get_context_data(self, **kwargs):
        """Pass app labels and the current group's permissions to the template."""
        context = super().get_context_data(**kwargs)

        group = get_object_or_404(Group, pk=self.kwargs['pk'])

        # Define apps to exclude
        excluded_apps = {'admin', 'auth', 'authentication', 'contenttypes', 'sessions'}

        # Get all unique app labels that have permissions, excluding certain apps
        all_app_labels = (
            ContentType.objects.filter(permission__isnull=False)
            .exclude(app_label__in=excluded_apps)
            .values_list('app_label', flat=True)
            .distinct()
        )

        # Get the app labels for the group's current permissions
        group_permissions = group.permissions.all()
        group_app_labels = group_permissions.values_list('content_type__app_label', flat=True).distinct()

        context.update({
            'group': group,
            'all_app_labels': sorted(all_app_labels),  # Sort alphabetically for better UX
            'group_app_labels': group_app_labels,
        })
        return context

    def post(self, request, *args, **kwargs):
        group = get_object_or_404(Group, pk=self.kwargs['pk'])
        selected_apps = request.POST.getlist('apps')

        if not selected_apps:
            messages.error(request, "No apps were selected. Please select at least one app.")
            return redirect('permissions:edit_group_permissions', pk=group.pk)

        # Clear all current permissions
        group.permissions.clear()

        # Add permissions for the selected app labels
        for app_label in selected_apps:
            app_permissions = Permission.objects.filter(content_type__app_label=app_label)
            group.permissions.add(*app_permissions)

        messages.success(request, f"Permissions for group '{group.name}' were successfully updated.")
        return redirect('permissions:groups_permissions')


class DeleteGroupView(DeleteView):
    model = Group
    success_url = reverse_lazy('permissions:groups_permissions')
  
    def delete(self, request, *args, **kwargs):
        group = self.get_object()
        group_name = group.name

        # Get all users belonging to this group
        users = CustomUser.objects.filter(groups=group)

        # Delete all users in the group
        user_count = users.count()
        users.delete()

        # Delete the group itself
        group.delete()

        # Add a success message
        messages.success(request, f"The group '{group_name}' and its {user_count} users have been deleted.")

        return redirect(self.success_url)
    
    
    


class AddGroupView(TemplateView):
    template_name = "permissions/addgroup.html"

    def get_context_data(self, **kwargs):
        """Provide a list of app labels with permissions to the template."""
        context = super().get_context_data(**kwargs)

        # Define apps to exclude
        excluded_apps = {'admin', 'auth', 'authentication', 'contenttypes', 'sessions'}

        # Get all unique app labels that have permissions, excluding certain apps
        all_app_labels = (
            ContentType.objects.filter(permission__isnull=False)
            .exclude(app_label__in=excluded_apps)
            .values_list('app_label', flat=True)
            .distinct()
        )

        context['all_app_labels'] = sorted(all_app_labels)  # Sort alphabetically for better UX
        return context

    def post(self, request, *args, **kwargs):
        """Handle group creation and assign permissions based on selected apps."""
        group_name = request.POST.get("group_name")
        selected_apps = request.POST.getlist("apps")

        if not group_name:
            messages.error(request, "Group name is required.")
            return redirect("permissions:add_group")

        # Create the new group
        group = Group.objects.create(name=group_name)

        # Add permissions for the selected app labels
        for app_label in selected_apps:
            app_permissions = Permission.objects.filter(content_type__app_label=app_label)
            group.permissions.add(*app_permissions)

        messages.success(request, f"Group '{group_name}' created successfully with permissions for selected apps.")
        return redirect("permissions:groups_permissions")  # Update this with your actual group list view name
