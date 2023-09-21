from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from .forms import LoginForm, SignUpForm, ProductForm, PurchaseForm, ReviewForm
from .models import Product, Purchase, Review, Category, Brand


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
    purchase_form = PurchaseForm()
    review_form = ReviewForm()
    reviews = Review.objects.filter(product=product)
    context = {'product': product, 'purchase_form':  purchase_form, 'review_form':  review_form, 'reviews': reviews}
    return render(request, 'product_detail.html', context)


def purchase_new(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.user = request.user
            purchase.product = product
            purchase.save()
            return redirect('product_detail', pk=pk)
    return redirect('product_detail', pk=pk)


def review_new(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', pk=pk)
    return redirect('product_detail', pk=pk)


def product_list(request):
    products = Product.objects.order_by("brand__title", "title")
    paginator = Paginator(products, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'product_list.html', context)


def user_purchase(request, username):
    profile = User.objects.get(username=username)
    purchases = Purchase.objects.filter(user=profile)
    context = {'profile': profile, 'purchases': purchases}
    return render(request, 'user_purchase.html', context)


def user_review(request, username):
    profile = User.objects.get(username=username)
    reviews = Review.objects.filter(user=profile)
    context = {'profile': profile, 'reviews': reviews}
    return render(request, 'user_review.html', context)


def category_view(request, pk):
    category = Category.objects.get(pk=pk)
    products = Product.objects.filter(category=category)
    context = {'category': category, 'products': products}
    return render(request, 'category.html', context)


def brand_view(request, pk):
    brand = Brand.objects.get(pk=pk)
    products = Product.objects.filter(brand=brand)
    context = {'brand': brand, 'products': products}
    return render(request, 'brand.html', context)


def search_view(request):
    query = request.GET.get('q')
    products = Product.objects.filter(Q(title__icontains=query) | Q(brand__title__icontains=query) | Q(category__title__icontains=query))
    context = {'query': query, 'products': products}
    return render(request, 'search.html', context)
