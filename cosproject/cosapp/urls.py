from django.urls import path
from . import views

urlpatterns = [
    path('product/new/', views.product_new, name='product_new'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/purchase/', views.purchase_new, name='purchase_new'),
    path('', views.product_list, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout')
]
