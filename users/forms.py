from django.contrib.auth.models import Group
from django import forms
from django.core.exceptions import ValidationError
from authentication.models import CustomUser
from django.contrib.auth.models import Permission

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password', 'role']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control form-select form-control-lg'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        email = cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            self.add_error('email', "A user with this email already exists.")

        return cleaned_data

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if self.cleaned_data["role"] == "admin":
            user.is_superuser = True
            user.is_staff = True

            all_permissions = Permission.objects.all()
            user.user_permissions.add(*all_permissions)
        if commit:
            user.save()

        # Assign the user to the appropriate group based on their role
        if self.cleaned_data["role"] == "cashier":
            cashier_group = Group.objects.get(name="cashier")
            user.groups.add(cashier_group)
        elif self.cleaned_data["role"] == "manager":
            manager_group = Group.objects.get(name="manager")
            user.groups.add(manager_group)

        elif self.cleaned_data["role"] == "admin":
                user.is_superuser = True
                user.is_staff = True
                admin_group = Group.objects.get(name="admin")
                user.groups.add(admin_group)
                all_permissions = Permission.objects.all()
                user.user_permissions.add(*all_permissions)

        return user






class EditUserForm(forms.ModelForm):
    password = forms.CharField(
        required=False, 
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='New Password'
    )
    confirm_password = forms.CharField(
        required=False, 
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm New Password'
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'role']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control form-select form-control-lg'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        email = cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exclude(id=self.instance.id).exists():
            self.add_error('email', "A user with this email already exists.")

        return cleaned_data

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password and len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return password
    def save(self, commit=True):
        user = super().save(commit=False)

        if self.cleaned_data["password"]:
            user.set_password(self.cleaned_data["password"])

        # Handle role changes (if any)
        if self.cleaned_data.get("role"):
            # Remove the user from previous groups
            user.groups.clear()

            if self.cleaned_data["role"] == "admin":
                user.is_superuser = True
                user.is_staff = True
                admin_group, created = Group.objects.get_or_create(name="admin")
                user.groups.add(admin_group)
            elif self.cleaned_data["role"] == "cashier":
                cashier_group, created = Group.objects.get_or_create(name="cashier")
                user.groups.add(cashier_group)
                print("role added")
            elif self.cleaned_data["role"] == "manager":
                manager_group, created = Group.objects.get_or_create(name="manager")
                user.groups.add(manager_group)

        if commit:
            user.save()

        return user

