from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=100)
    registration_number = forms.CharField(max_length=20)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'registration_number', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def clean_registration_number(self):
        reg_num = self.cleaned_data.get('registration_number')
        if User.objects.filter(registration_number=reg_num).exists():
            raise forms.ValidationError("This registration number is already registered.")
        return reg_num


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150)  # Use 'username' instead of 'registration_number'
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'full_name']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email