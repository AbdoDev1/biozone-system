from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ClientProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'status', 'is_active')
    list_filter = ('role', 'status')
    fieldsets = UserAdmin.fieldsets + (
        ('بيانات إضافية', {'fields': ('role', 'status')}),
    )


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'business_type', 'user', 'phone')
    list_filter = ('business_type',)
