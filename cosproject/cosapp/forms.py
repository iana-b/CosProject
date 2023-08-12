from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Product


class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField()


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
