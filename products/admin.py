from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Product, ProductUnit


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class ProductUnitInline(admin.TabularInline):
    model = ProductUnit
    extra = 3
    fields = ('size', 'name', 'qty_in_small', 'unit_price', 'wholesale_min_qty', 'wholesale_price', 'wholesale_mode')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'manufacturer', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'manufacturer')
    inlines = [ProductUnitInline]
