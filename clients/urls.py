from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.client_list, name='list'),
    path('<int:pk>/', views.client_detail, name='detail'),
    path('<int:pk>/approve/', views.client_approve, name='approve'),
    path('<int:pk>/reject/', views.client_reject, name='reject'),
]

