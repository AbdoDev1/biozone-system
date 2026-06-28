from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from inventory.models import Inventory, StockMovement


def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('staff:login')
        if request.user.role not in ['ADMIN', 'WAREHOUSE']:
            return redirect('staff:login')
        return view_func(request, *args, **kwargs)
    return wrapper


@staff_required
def inventory_list(request):
    items = Inventory.objects.select_related(
        'product_unit__product__category'
    ).all().order_by('product_unit__product__name_ar')
    return render(request, 'staff/inventory/list.html', {'items': items})


@staff_required
def inventory_detail(request, pk):
    item = get_object_or_404(Inventory, pk=pk)
    movements = item.movements.select_related('created_by').order_by('-created_at')[:20]
    return render(request, 'staff/inventory/detail.html', {
        'item': item,
        'movements': movements,
    })


@staff_required
def add_movement(request, pk):
    item = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        movement_type = request.POST.get('movement_type')
        quantity = int(request.POST.get('quantity', 0))
        note = request.POST.get('note', '')
        if quantity <= 0:
            messages.error(request, 'الكمية يجب أن تكون أكبر من صفر')
            return redirect('staff:inventory_detail', pk=pk)
        StockMovement.objects.create(
            inventory=item,
            movement_type=movement_type,
            quantity=quantity,
            note=note,
            created_by=request.user,
        )
        messages.success(request, 'تم تسجيل الحركة بنجاح')
        return redirect('staff:inventory_detail', pk=pk)
    return redirect('staff:inventory_detail', pk=pk)
