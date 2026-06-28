from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Inventory, StockMovement


class StockMovementInline(admin.TabularInline):
    model = StockMovement
    extra = 1
    fields = ('movement_type', 'quantity', 'note', 'created_by')
    readonly_fields = ('created_at',)


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product_unit', 'quantity', 'reserved', 'available', 'min_quantity', 'is_low')
    list_filter = ('product_unit__product__category',)
    search_fields = ('product_unit__product__name',)
    readonly_fields = ('available', 'updated_at')
    inlines = [StockMovementInline]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('inventory', 'movement_type', 'quantity', 'created_by', 'created_at')
    list_filter = ('movement_type',)
    readonly_fields = ('created_at',)
