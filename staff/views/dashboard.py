from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models as django_models
from inventory.models import Inventory
from clients.models import ClientProfile


def staff_login(request):
    if request.user.is_authenticated:
        if request.user.role in ['ADMIN', 'WAREHOUSE']:
            return redirect('staff:dashboard')
        return redirect('accounts:login')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.role in ['ADMIN', 'WAREHOUSE']:
            login(request, user)
            return redirect('staff:dashboard')
        else:
            messages.error(request, 'بيانات غلط أو مش موظف')

    return render(request, 'staff/login.html')


def staff_logout(request):
    logout(request)
    return redirect('staff:login')


@login_required(login_url='/staff/login/')
def dashboard(request):
    if request.user.role not in ['ADMIN', 'WAREHOUSE']:
        return redirect('staff:login')

    low_stock = Inventory.objects.filter(
        quantity__lte=django_models.F('min_quantity')
    ).select_related('product_unit__product')[:5]

    pending_clients = ClientProfile.objects.filter(
        user__status='PENDING'
    ).count()

    total_products = Inventory.objects.count()

    return render(request, 'staff/dashboard.html', {
        'low_stock': low_stock,
        'pending_clients': pending_clients,
        'total_products': total_products,
    })
