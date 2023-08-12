from django.urls import path
from . import views

urlpatterns = [
    path('product/new/', views.product_new, name='product_new'),
]
