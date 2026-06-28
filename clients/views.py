from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from accounts.models import User, ClientProfile


def client_list(request):
    pending = ClientProfile.objects.filter(user__status='PENDING').select_related('user')
    active = ClientProfile.objects.filter(user__status='ACTIVE').select_related('user')
    rejected = ClientProfile.objects.filter(user__status='REJECTED').select_related('user')
    return render(request, 'clients/list.html', {
        'pending': pending,
        'active': active,
        'rejected': rejected,
    })


def client_detail(request, pk):
    profile = get_object_or_404(ClientProfile, pk=pk)
    return render(request, 'clients/detail.html', {'profile': profile})


def client_approve(request, pk):
    profile = get_object_or_404(ClientProfile, pk=pk)
    user = profile.user
    user.status = User.Status.ACTIVE
    user.is_active = True
    profile.verified_at = timezone.now()
    user.save()
    profile.save()
    messages.success(request, f'تم تفعيل حساب {profile.business_name}')
    return redirect('clients:list')


def client_reject(request, pk):
    profile = get_object_or_404(ClientProfile, pk=pk)
    user = profile.user
    user.status = User.Status.REJECTED
    user.is_active = False
    user.save()
    messages.error(request, f'تم رفض حساب {profile.business_name}')
    return redirect('clients:list')
