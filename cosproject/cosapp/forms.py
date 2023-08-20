from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.text import capfirst

from .models import Product, Purchase, Review


class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=255, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class PurchaseForm(forms.ModelForm):
    date = forms.DateField(
        label=capfirst(Purchase.date.field.verbose_name), required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    store = forms.CharField(label=capfirst(Purchase.store.field.verbose_name), required=False)

    class Meta:
        model = Purchase
        exclude = ('user', 'product')


class ReviewForm(forms.ModelForm):
    comment = forms.CharField(label=capfirst(Review.comment.field.verbose_name), widget=forms.Textarea, required=False)

    class Meta:
        model = Review
        exclude = ('user', 'product')
