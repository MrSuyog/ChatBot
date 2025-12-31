
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

six_alnum = RegexValidator(
    regex=r'^[A-Za-z0-9]{6}$',
    message='Must be exactly 6 characters (letters or digits only).'
)

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label='Username',
        min_length=6,
        max_length=6,
        validators=[six_alnum],
        help_text='Exactly 6 letters or digits (e.g., user12, abc123).'
    )
    first_name = forms.CharField(max_length=30, required=True, label="First name")
    last_name  = forms.CharField(max_length=30, required=True, label="Last name")
    email      = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name  = self.cleaned_data["last_name"]
        user.email      = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username',
        min_length=6,
        max_length=6,
        validators=[six_alnum],
        help_text='Exactly 6 letters or digits.'
    )