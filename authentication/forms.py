from django import forms
from django.contrib.auth import authenticate
from  .models import CustomUser

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'email',
            'placeholder': 'Enter Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password'
        })
    )
    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        self.user = authenticate(username=email, password=password)

        if not self.user:
            raise forms.ValidationError("Invalid email or password.")
        return cleaned_data

    def get_user(self):
        return self.user




