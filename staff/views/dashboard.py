from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from inventory.models import Inventory
from clients.models import ClientProfile


def staff_login(request):
    if request.user.is_authenticated:
        if request.user.role in ['ADMIN', 'WAREHOUSE']:
            return redirect('staff:dashboard')
        return redirect('catalog:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.role in ['ADMIN', 'WAREHOUSE']:
                login(request, user)
                return redirect('staff:dashboard')
            else:
                messages.error(request,  'يرجى الدخول من صفحة  العملاء.')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غلط.')

    return render(request, 'staff/login.html')


def staff_logout(request):
    logout(request)
    return redirect('staff:login')

@login_required
def dashboard(request):
    if request.user.role not in ['ADMIN', 'WAREHOUSE']:
        return redirect('catalog:home')

    total_products = Inventory.objects.count()
    low_stock = Inventory.objects.filter(quantity__lte=django_models_F('min_quantity')).count() \
        if False else Inventory.objects.all()
    pending_clients = ClientProfile.objects.filter(user__status='PENDING').count()

    context = {
        'total_products': total_products,
        'pending_clients': pending_clients,
    }
    return render(request, 'staff/dashboard.html', context)
