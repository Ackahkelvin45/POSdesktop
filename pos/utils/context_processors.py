from django.contrib.auth.models import Permission

def app_permissions(request):
    """
    Adds detailed permissions for the user's groups to the context.
    """
    if request.user.is_authenticated:
        user_groups = request.user.groups.all()
        group_permissions = Permission.objects.filter(group__in=user_groups)
        permissions = group_permissions.values_list('content_type__app_label', 'codename')
        permissions_dict = {}

        for app_label, codename in permissions:
            permissions_dict.setdefault(app_label, []).append(codename)

        return {"user_app_permissions": permissions_dict}
    return {"user_app_permissions": {}}
