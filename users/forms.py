from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'first_name', 'last_name', 'user_type', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove user_type field for regular registration
        if 'user_type' in self.fields:
            del self.fields['user_type']

        # Add Bootstrap classes and placeholders to all fields
        for field_name, field in self.fields.items():
            if field_name in ['password1', 'password2']:
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Create a strong password' if field_name == 'password1' else 'Confirm your password'
                })
            elif field_name == 'username':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Choose a unique username'
                })
            elif field_name == 'email':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Enter your email address'
                })
            elif field_name in ['first_name', 'last_name']:
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': f'Enter your {field_name.replace("_", " ")}'
                })
            elif field_name == 'phone_number':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Enter your phone number (optional)'
                })

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'address', 'date_of_birth', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'date_of_birth':
                self.fields[field].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class StaffUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'user_type', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': {
                    'old_password': 'Enter your current password',
                    'new_password1': 'Enter your new password',
                    'new_password2': 'Confirm your new password'
                }.get(field, '')
            })
