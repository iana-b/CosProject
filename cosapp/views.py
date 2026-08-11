from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import (
    Avg,
    Count,
    Min,
    Q,
)
from django.db.models.functions import TruncDate
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import LoginForm, SignUpForm, ProductForm, PurchaseForm, ReviewForm
from .middleware import hash_ip
from .models import Product, Purchase, Review, Category, Brand, PageView

SIGNUPS_PER_HOUR = 3


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
    key = f'signups:{hash_ip(request)}'
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if cache.get(key, 0) >= SIGNUPS_PER_HOUR:
            form.add_error(None, 'Слишком много регистраций с этого адреса. Попробуйте позже.')
        elif form.is_valid():
            form.save()
            cache.set(key, cache.get(key, 0) + 1, 3600)
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


@login_required
def product_new(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.status = Product.PUBLISHED if request.user.is_staff else Product.DRAFT
            product.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    context = {'form': form}
    return render(request, 'product_edit.html', context)


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.annotate(
            avg_rating=Avg("review__rating"),
            min_price=Min("purchase__price"),
        ).select_related("brand", "category"),
        pk=pk,
    )
    if not product.is_visible_to(request.user):
        raise Http404
    request.viewed_product = product
    purchase_form = PurchaseForm()
    review_form = ReviewForm()
    reviews = Review.objects.filter(product=product).select_related("user")
    purchases = Purchase.objects.filter(product=product)
    context = {
        "product": product,
        "purchase_form": purchase_form,
        "review_form": review_form,
        "reviews": reviews,
        "avg_rating": product.avg_rating or 0,
        "purchases": purchases,
    }
    return render(request, "product_detail.html", context)


@login_required
def purchase_new(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.user = request.user
            purchase.product = product
            purchase.save()
            return redirect('product_detail', pk=pk)
    return redirect('product_detail', pk=pk)


@login_required
def review_new(request, pk):
    product = get_object_or_404(Product, pk=pk)
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
    products = _products_queryset()
    paginator = Paginator(products, 16)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'product_list.html', context)


def user_purchase(request, username):
    profile = get_object_or_404(User, username=username)
    purchases = Purchase.objects.filter(user=profile)
    context = {'profile': profile, 'purchases': purchases}
    return render(request, 'user_purchase.html', context)


def user_review(request, username):
    profile = get_object_or_404(User, username=username)
    reviews = Review.objects.filter(user=profile)
    context = {'profile': profile, 'reviews': reviews}
    return render(request, 'user_review.html', context)


def _products_queryset(queryset=None):
    """Базовый queryset опубликованных товаров с брендом, категорией, рейтингом и ценой — без N+1."""
    qs = queryset if queryset is not None else Product.objects.all()
    return qs.filter(status=Product.PUBLISHED).select_related("brand", "category").annotate(
        avg_rating=Avg("review__rating"),
        min_price=Min("purchase__price"),
    ).order_by("brand__title", "title")


def category_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = _products_queryset(Product.objects.filter(category=category))
    context = {'category': category, 'products': products}
    return render(request, 'category.html', context)


def brand_view(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    products = _products_queryset(Product.objects.filter(brand=brand))
    context = {'brand': brand, 'products': products}
    return render(request, 'brand.html', context)


def search_view(request):
    query = request.GET.get('q', '').strip()
    products = _products_queryset(
        Product.objects.filter(
            Q(title__icontains=query)
            | Q(brand__title__icontains=query)
            | Q(category__title__icontains=query)
        )
    ) if query else Product.objects.none()
    context = {'query': query, 'products': products}
    return render(request, 'search.html', context)


@staff_member_required
def stats_view(request):
    since = timezone.now() - timedelta(days=30)
    views = PageView.objects.filter(created_at__gte=since)
    by_day = (
        views.annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(views=Count('id'), visitors=Count('ip_hash', distinct=True))
        .order_by('day')
    )
    by_day = list(by_day)
    peak = max((d['views'] for d in by_day), default=0)
    for day in by_day:
        day['share'] = round(day['views'] * 100 / peak) if peak else 0
    top_products = (
        views.filter(product__isnull=False)
        .values('product_id', 'product__title', 'product__brand__title')
        .annotate(views=Count('id'))
        .order_by('-views')[:10]
    )
    context = {
        'by_day': by_day,
        'top_products': top_products,
        'recent': PageView.objects.select_related('user', 'product')[:50],
        'total_views': views.count(),
        'total_visitors': views.values('ip_hash').distinct().count(),
        'pending': Product.objects.filter(status=Product.DRAFT).count(),
    }
    return render(request, 'stats.html', context)
