from .models import GlobalActivityLog  
def log_activity(user, action, model_name, notes=None):
    """
    Utility to log user actions into the GlobalActivityLog.
    """
# Avoid circular imports
    GlobalActivityLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        notes=notes
    )
