from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from .forms import LoginForm, SignUpForm, ProductForm, PurchaseForm
from .models import Product


# Create your views here.
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    context = {'form': form}
    return render(request, 'signup.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')


def product_new(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    context = {'form': form}
    return render(request, 'product_edit.html', context)


def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.user = request.user
            purchase.product = product
            purchase.save()
            return redirect('product_detail', pk=pk)
    else:
        form = PurchaseForm()
    context = {'product': product, 'form': form}
    return render(request, 'product_detail.html', context)


def product_list(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'product_list.html', context)
