from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog_home, name='home'),
    path('search/', views.catalog_search, name='search'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
]
