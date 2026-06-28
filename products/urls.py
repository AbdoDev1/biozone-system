from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('<path:slug>/', views.category_detail, name='category_detail'),
    path('item/<int:pk>/', views.product_detail, name='product_detail'),
]
