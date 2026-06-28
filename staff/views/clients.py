from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.models import User, ClientProfile


def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('staff:login')
        if request.user.role not in ['ADMIN', 'WAREHOUSE']:
            return redirect('staff:login')
        return view_func(request, *args, **kwargs)
    return wrapper


@staff_required
def client_list(request):
    pending = ClientProfile.objects.filter(user__status='PENDING').select_related('user')
    active = ClientProfile.objects.filter(user__status='ACTIVE').select_related('user')
    rejected = ClientProfile.objects.filter(user__status='REJECTED').select_related('user')
    return render(request, 'staff/clients/list.html', {
        'pending': pending,
        'active': active,
        'rejected': rejected,
    })


@staff_required
def client_detail(request, pk):
    profile = get_object_or_404(ClientProfile, pk=pk)
    return render(request, 'staff/clients/detail.html', {'profile': profile})


@staff_required
def client_approve(request, pk):
    profile = get_object_or_404(ClientProfile, pk=pk)
    user = profile.user
    user.status = User.Status.ACTIVE
    user.is_active = True
    profile.verified_at = timezone.now()
    user.save()
    profile.save()
    messages.success(request, f'تم تفعيل حساب {profile.business_name}')
    return redirect('staff:clients')


@staff_required
def client_reject(request, pk):
    profile = get_object_or_404(ClientProfile, pk=pk)
    user = profile.user
    user.status = User.Status.REJECTED
    user.is_active = False
    user.save()
    messages.error(request, f'تم رفض حساب {profile.business_name}')
    return redirect('staff:clients')
