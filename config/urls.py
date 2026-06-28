from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect, render

def home(request):
    if request.user.is_authenticated:
        if request.user.role in ['ADMIN', 'WAREHOUSE']:
            return redirect('staff:dashboard')
        return redirect('accounts:dashboard')
    return render(request, 'landing.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('clients/', include('clients.urls')),
    path('products/', include('products.urls')),
    path('inventory/', include('inventory.urls')),
    path('staff/', include('staff.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
