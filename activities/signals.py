# signals.py
from django.db.models.signals import pre_save, post_save,post_delete,m2m_changed
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
from product.signals import reset_quantities_signal,delete_quantities_signal,delete_all_category_signal
from inventory.models import  InventoryLog
from django.contrib.auth.models import Permission


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
        notes = f"Inventory action {action} created for {instance.product.name}. Quantity: {instance.quantity}"
 
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
    if Product.is_resetting():
        return
    if Product.is_reversing_available_quantity():
        return
    # Get the logged-in user (passed via middleware)
    user = get_current_user()

    # Check if the instance already exists in the database (i.e., it's being updated)
    try:
        original_instance = Product.objects.get(id=instance.id)
        updated_fields = []

        if original_instance.available_quantity != instance.available_quantity:
            # Compare the original and new values of available_quantity
            action=""
            notes=''
            if instance.available_quantity > original_instance.available_quantity:
                quantity_change = f"increased from {original_instance.available_quantity} to {instance.available_quantity}"
                action="updated manually(add)"
                notes=f' The product was manually updated in the edit product form. The available quantity was increased by {abs(instance.available_quantity - original_instance.available_quantity)}. '
            else:
                quantity_change = f"decreased from {original_instance.available_quantity} to {instance.available_quantity}"
                action="updated manually(remove)"
                notes=f'The Product was manually updated in the edit product form.The available quantity was reduced by {abs(instance.available_quantity-original_instance.available_quantity)}  '

            quantity=abs(instance.available_quantity-original_instance.available_quantity)
            inventorylog=InventoryLog(product=instance, quantity=quantity,action=action,new_quantity=instance.available_quantity, previous_quantity=original_instance.available_quantity,notes=notes)
            inventorylog.save_default()
            
        # List of fields to check for changes
        fields_to_check = ['name', 'description', 'unit_selling_price', 'unit_cost_price', 'bulk_selling_price', 'bulk_cost_price', 'category',  'image', 'units_per_bulk','available_quantity']

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
    if Product.is_deleting_all():
        return 
    user = get_current_user()
      
    notes = f"Product {instance.name}  is being deleted."
    log_activity(user=user, action='delete', model_name='Product', notes=notes)

# Pre-Delete log for ProductCategory deletion
@receiver(post_delete, sender=ProductCategory)
def log_product_category_deletion(sender, instance, **kwargs):
    if ProductCategory.is_deleting_all():
        return 
    user = get_current_user()
      
    notes = f"Product Category {instance.name} is being deleted."
    log_activity(user=user, action='delete', model_name='ProductCategory', notes=notes)




@receiver(post_delete, sender=InventoryLog)
def log_product_category_deletion(sender, instance, **kwargs):
    user = get_current_user()
      
    notes = f"Inventory Log.{instance.product.name} Quantity has been reversed by {instance.quantity} "
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
        fields_to_check = ['name']

        # Compare simple fields
        for field in fields_to_check:
            original_value = getattr(original_instance, field)
            current_value = getattr(instance, field)
            if original_value != current_value:
                updated_fields.append(f"{field}: {original_value} to {current_value}")

        # Compare many-to-many fields (permissions)
        original_permissions = set(original_instance.permissions.all())
        current_permissions = set(instance.permissions.all())
        if original_permissions != current_permissions:
            added = current_permissions - original_permissions
            removed = original_permissions - current_permissions

            if added:
                updated_fields.append(f"permissions added: {', '.join(p.name for p in added)}")
            if removed:
                updated_fields.append(f"permissions removed: {', '.join(p.name for p in removed)}")

        # If fields were updated, log the details
        if updated_fields:
            action = 'update'
            notes = f"Group '{instance.name}' has been updated. Fields changed: {', '.join(updated_fields)}"
        else:
            action = 'update'
            notes = f"Group '{instance.name}' has been updated, but no fields changed."

        log_activity(
            user=user,
            action=action,
            model_name='Group',
            notes=notes,
        )

 



    except Group.DoesNotExist:
        # If it's a new group (doesn't exist in the database yet), log creation
        action = 'create'
        notes = f"Group '{instance.name}' has been created."

      

        log_activity(  user=user,
            action=action,
            model_name='Group',
            notes=notes,
            )
# Post delete signal to track group deletion
@receiver(post_delete, sender=Group)
def group_post_delete(sender, instance, **kwargs):
    user = get_current_user()
      
 

    # Log the deletion
    notes = f"Group '{instance.name}' has been deleted."

    log_activity(  user=user,
            action="delte",
            model_name='Group',
            notes=notes,
            )

@receiver(reset_quantities_signal)
def log_resetall_product(sender, user, **kwargs):
    notes = f"All product quantities were reset to zero."

    
    log_activity(  user=user,
            action="reset all to zero",
            model_name='Product',
            notes=notes,
            )
    
@receiver(delete_quantities_signal)
def log_deleteall_product(sender, user, **kwargs):
    notes = f"All products deleted."

    
    log_activity(  user=user,
            action="delete all ",
            model_name='Product',
            notes=notes,
            )

@receiver(delete_all_category_signal)
def log_deleteall_category(sender, user, **kwargs):
    notes = f"All product category deleted."

    
    log_activity(  user=user,
            action="delete all ",
            model_name='Product Category',
            notes=notes,
            )
    

@receiver(m2m_changed, sender=Group.permissions.through)
def log_group_permissions_change(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Log changes to the Group's permissions field.
    """
    user = get_current_user()  # Get the user performing the action

    if action in ['post_add', 'post_remove', 'post_clear']:
        changes = []

        if action == 'post_add':
            permissions = Permission.objects.filter(pk__in=pk_set)
            changes = [f"Added: '{perm.name}'" for perm in permissions]

        elif action == 'post_remove':
            permissions = Permission.objects.filter(pk__in=pk_set)
            changes = [f"Removed: '{perm.name}'" for perm in permissions]

        elif action == 'post_clear':
            changes = ["All permissions were cleared."]

        if changes:
            formatted_changes = "\n".join(changes)
            notes = (
                f"Group Permissions Update:\n"
                f"Group: '{instance.name}'\n"
                f"Changes:\n{formatted_changes}"
            )
            log_activity(
                user=user,
                action='Permission Update',
                model_name='Group',
                notes=notes,
            )
