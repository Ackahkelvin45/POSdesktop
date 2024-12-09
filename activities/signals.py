# signals.py
from django.db.models.signals import pre_save, post_save,post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from authentication.models import  CustomUser
from .models  import GlobalActivityLog
from inventory.models import InventoryLog
from product.models import Product,ProductCategory
from django.contrib.auth.signals import user_logged_in, user_logged_out,user_login_failed
from .utils import log_activity
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


from .middleware import get_current_user


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    log_activity(
        user=user,
        action='login',
        model_name='User',
        
        notes="User logged in"
    )

# Log when a user logs out
@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    log_activity(
        user=user,
        action='logout',
        model_name='User',
       
        notes="User logged out"
    )
    
@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    # Get the username and IP address from the request
    username = credentials.get('email', 'unknown')
    ip_address = request.META.get('REMOTE_ADDR', 'unknown')
    
    # Log the failed login attempt
    notes = f"Failed login attempt for user '{username}' from IP address {ip_address}."
    log_activity(user=None, action='login_failed', model_name='User', notes=notes)
    
@receiver(pre_save, sender=CustomUser)
def log_user_creation_or_update(sender, instance, **kwargs):
    """
    Log activity for user creation or update with detailed field changes.
    """
    user = get_current_user()
    
    try:
        # Fetch the original instance from the database to compare
        original_instance = CustomUser.objects.get(id=instance.id)
        updated_fields = []

        # List of fields you want to check for updates
        fields_to_check = ['email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff']

        for field in fields_to_check:
            original_value = getattr(original_instance, field)
            current_value = getattr(instance, field)
            if original_value != current_value:
                updated_fields.append(f"{field}: {original_value}  to {current_value}")

        # If fields were updated, log the details of the changes
        if updated_fields:
            notes = f"User updated. Fields changed: {', '.join(updated_fields)}"
            action = 'update'
        else:
            notes = "User updated, but no fields changed."
            action = 'update'

        # Log the activity with detailed field changes
        GlobalActivityLog.objects.create(
            user=user,
            action=action,
            model_name='CustomUser',
            notes=notes,
            timestamp=now()
        )

    except CustomUser.DoesNotExist:
        # If it's a new user (doesn't exist in the database yet), log creation
        notes = "User created"
        action = 'create'
        
        GlobalActivityLog.objects.create(
            user=user,
            action=action,
            model_name='CustomUser',
            notes=notes,
            timestamp=now()
        )


@receiver(post_save, sender=InventoryLog)
def log_inventory_action(sender, instance, created, **kwargs):
    """
    Log activity for inventory actions (add, remove, sale) with detailed field changes.
    """
    action = instance.action
    notes = ""
    user = get_current_user()
      
    
    if created:
        # Log inventory action creation
        notes = f"Inventory action {action} created. Quantity: {instance.quantity}"
 
    # Log the action in GlobalActivityLog
    GlobalActivityLog.objects.create(
        user=user,  # Assuming you have a field like `created_by` for the user who performed the action.
        action=action,
        model_name='InventoryLog',
        notes=notes,
        timestamp=now()
    )





    
    

@receiver(pre_save, sender=Product)
def log_product_creation_or_update(sender, instance, **kwargs):
    # Get the logged-in user (passed via middleware)
    user = get_current_user()

    # Check if the instance already exists in the database (i.e., it's being updated)
    try:
        original_instance = Product.objects.get(id=instance.id)
        updated_fields = []

        # List of fields to check for changes
        fields_to_check = ['name', 'description', 'unit_selling_price', 'unit_cost_price', 'bulk_selling_price', 'bulk_cost_price', 'category', 'available_quantity', 'image', 'units_per_bulk']

        # Compare original values with the new instance values
        for field in fields_to_check:
            original_value = getattr(original_instance, field)
            current_value = getattr(instance, field)
            if original_value != current_value:
                updated_fields.append(f"{field}: {original_value}  to {current_value}")

        if updated_fields:
            notes = f"Product {instance.name} updated. Fields changed: {', '.join(updated_fields)}"
        else:
            notes = f"Product {instance.name} updated, but no fields changed."

        # Store the action type
        action = 'update'

    except Product.DoesNotExist:
        # If it's a new instance, no need to compare fields, just log creation
        notes = f"Product {instance.name} created."
        action = 'create'

    # Assuming you have a log_activity function to track the changes
    log_activity(user=user, action=action, model_name='Product', notes=notes)


# Log for ProductCategory creation and updates
@receiver(pre_save, sender=ProductCategory)
def log_product_category_creation_or_update(sender, instance, **kwargs):
    # Get the logged-in user from middleware
    user = get_current_user()

    try:
        # Fetch the original instance from the database to compare
        original_instance = ProductCategory.objects.get(id=instance.id)
        updated_fields = []

        # Fields to track
        fields_to_check = ['name', 'description']

        for field in fields_to_check:
            original_value = getattr(original_instance, field)
            current_value = getattr(instance, field)
            if original_value != current_value:
                updated_fields.append(f"{field}: {original_value} to {current_value}")
        
        if updated_fields:
            notes = f"Product Category {instance.name} updated. Fields changed: {', '.join(updated_fields)}"
            action = 'update'
        else:
            notes = f"Product Category {instance.name} updated, but no fields changed."
            action = 'update'

    except ProductCategory.DoesNotExist:
        # Handle the case where the category does not exist (i.e., it's a new category)
        notes = f"Product Category {instance.name} created."
        action = 'create'

    # Log the activity
    log_activity(user=user, action=action, model_name='ProductCategory', notes=notes)




# Pre-Delete log for CustomUser
@receiver(post_delete, sender=CustomUser)
def log_custom_user_deletion(sender, instance, **kwargs):
    user = get_current_user()
      
    notes = f"User {instance.first_name} {instance.last_name} (Email: {instance.email}) is being deleted."
    log_activity(user=user, action='delete', model_name='CustomUser', notes=notes)

# Pre-Delete log for Product deletion
@receiver(post_delete, sender=Product)
def log_product_deletion(sender, instance, **kwargs):
    user = get_current_user()
      
    notes = f"Product {instance.name} (ID: {instance.id}) is being deleted."
    log_activity(user=user, action='delete', model_name='Product', notes=notes)

# Pre-Delete log for ProductCategory deletion
@receiver(post_delete, sender=ProductCategory)
def log_product_category_deletion(sender, instance, **kwargs):
    user = get_current_user()
      
    notes = f"Product Category {instance.name} is being deleted."
    log_activity(user=user, action='delete', model_name='ProductCategory', notes=notes)




@receiver(post_delete, sender=ProductCategory)
def log_product_category_deletion(sender, instance, **kwargs):
    user = get_current_user()
      
    notes = f"Inventory Log.{instance.product.name} Quantity has been reversed by {instance.qauntity} "
    log_activity(user=user, action='reverse', model_name='Inventory', notes=notes)





@receiver(pre_save, sender=Group)
def group_pre_save(sender, instance, **kwargs):
    """
    Log activity for group creation or update, with detailed field changes.
    """
    user = get_current_user()  # Get the user performing the action

    try:
        # Fetch the original instance from the database to compare the current one
        original_instance = Group.objects.get(id=instance.id)
        updated_fields = []

        # List of fields you want to check for updates
        fields_to_check = ['name', 'description']  # Add other fields as needed

        # Compare each field between the original and the updated instance
        for field in fields_to_check:
            original_value = getattr(original_instance, field)
            current_value = getattr(instance, field)
            if original_value != current_value:
                updated_fields.append(f"{field}: {original_value} to {current_value}")

        # If fields were updated, log the details
        if updated_fields:
            action = 'update'
            notes = f"Group '{instance.name}' has been updated. Fields changed: {', '.join(updated_fields)}"
        else:
            action = 'update'
            notes = f"Group '{instance.name}' has been updated, but no fields changed."

        # Log the activity in the GlobalActivityLog
        GlobalActivityLog.objects.create(
            user=user,
            action=action,
            model_name='Group',
            notes=notes,
            timestamp=now()  # You can include a timestamp if needed
        )

    except Group.DoesNotExist:
        # If it's a new group (doesn't exist in the database yet), log creation
        action = 'create'
        notes = f"Group '{instance.name}' has been created."

        # Log the activity for the new group
        GlobalActivityLog.objects.create(
            user=user,
            action=action,
            model_name='Group',
            notes=notes,
            timestamp=now()  # You can include a timestamp if needed
        )
# Post delete signal to track group deletion
@receiver(post_delete, sender=Group)
def group_post_delete(sender, instance, **kwargs):
    user = get_current_user()
      
 

    # Log the deletion
    notes = f"Group '{instance.name}' has been deleted."
    GlobalActivityLog.objects.create(
        user=user,
        action='delete',
        model_name='Group',
     
        notes=notes,
        timestamp=now()
    )
