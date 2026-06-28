from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import models as django_models
from .forms import RegisterForm, LoginForm
from .models import User
from inventory.models import Inventory


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إرسال طلب التسجيل، انتظر موافقة الإدارة.')
            return redirect('accounts:pending')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user:
                if user.status == User.Status.PENDING:
                    messages.warning(request, 'حسابك في انتظار موافقة الإدارة.')
                    return redirect('accounts:pending')
                elif user.status == User.Status.REJECTED:
                    messages.error(request, 'تم رفض طلب تسجيلك.')
                else:
                    login(request, user)
                    return redirect('products:category_list')
            else:
                messages.error(request, 'اسم المستخدم أو كلمة المرور غلط.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')

def pending_view(request):
    return render(request, 'accounts/pending.html')


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if request.user.role in ['ADMIN', 'WAREHOUSE']:
        return redirect('staff:dashboard')
    return render(request, 'accounts/dashboard.html', {})
