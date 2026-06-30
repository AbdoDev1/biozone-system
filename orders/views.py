import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from products.models import ProductUnit
from inventory.models import Inventory, StockMovement
from .cart import Cart
from .models import Order, OrderItem, SiteConfig


def cart_add(request, unit_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'سجل دخولك أولاً.')
        return redirect('accounts:login')

    if request.user.role != 'CLIENT' or request.user.status != 'ACTIVE':
        messages.error(request, 'مش عندك صلاحية.')
        return redirect('catalog:home')

    cart = Cart(request)
    quantity = int(request.POST.get("quantity", 1))
    cart.add(unit_id, quantity)

    if request.headers.get("HX-Request"):
        unit = get_object_or_404(ProductUnit, pk=unit_id)
        # نرجع الزر المحدّث (أخضر) + نحرك event لتحديث الـ badge
        response = render(request, "orders/partials/add_button.html", {
            "unit": unit,
            "in_cart": True,
        })
        response['HX-Trigger'] = json.dumps({'cartUpdated': {'count': len(cart)}})
        return response

    return redirect(request.POST.get("next", "catalog:home"))


def cart_badge(request):
    cart = Cart(request)
    return render(request, 'orders/partials/cart_badge.html', {'count': len(cart)})


def cart_update(request, unit_id):
    cart = Cart(request)
    quantity = int(request.POST.get("quantity", 1))
    wholesale = request.POST.get("wholesale") == "on"
    cart.set_quantity(unit_id, quantity)
    cart.set_wholesale(unit_id, wholesale)
    if request.headers.get("HX-Request"):
        return cart_controls(request, unit_id)
    return redirect("orders:cart")


def cart_remove(request, unit_id):
    cart = Cart(request)
    cart.remove(unit_id)
    if request.headers.get("HX-Request"):
        return cart_controls(request, unit_id)
    return redirect("orders:cart")


def cart_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    cart = Cart(request)
    config = SiteConfig.get_solo()
    total = cart.get_total()
    remaining = config.min_order_amount - total if config.min_order_amount else 0
    return render(request, 'orders/cart.html', {
        'cart_items': cart.get_items(),
        'total': total,
        'min_order_amount': config.min_order_amount,
        'remaining_to_min': remaining if remaining > 0 else 0,
        'below_min': remaining > 0,
    })


def cart_plus(request, unit_id):
    cart = Cart(request)
    cart.increase(unit_id)
    return cart_controls(request, unit_id)


def cart_minus(request, unit_id):
    cart = Cart(request)
    cart.decrease(unit_id)
    return cart_controls(request, unit_id)


def cart_controls(request, unit_id):
    cart = Cart(request)
    quantity = cart.cart.get(str(unit_id), {}).get("quantity", 0)
    response = render(request, "orders/partials/cart_controls.html", {
        "unit_id": unit_id,
        "quantity": quantity,
    })
    response['HX-Trigger'] = json.dumps({'cartUpdated': {'count': len(cart)}})
    return response


@login_required
def checkout(request):
    if request.user.role != 'CLIENT' or request.user.status != 'ACTIVE':
        return redirect('catalog:home')

    cart = Cart(request)
    items = cart.get_items()

    if not items:
        messages.warning(request, 'سلتك فاضية.')
        return redirect('orders:cart')

    config = SiteConfig.get_solo()
    total = cart.get_total()

    if config.min_order_amount and total < config.min_order_amount:
        messages.error(
            request,
            f'الحد الأدنى لإجمالي الطلب هو {config.min_order_amount} ج.م. '
            f'إجمالي سلتك الحالي {total} ج.م، يلزم إضافة {config.min_order_amount - total} ج.م إضافية.'
        )
        return redirect('orders:cart')

    if request.method == 'POST':
        with transaction.atomic():
            unit_ids = [item['unit'].pk for item in items]
            locked_inventories = {
                inv.product_unit_id: inv
                for inv in Inventory.objects.select_for_update().filter(product_unit_id__in=unit_ids)
            }

            shortages = []
            for item in items:
                unit = item['unit']
                inv = locked_inventories.get(unit.pk)
                available = inv.available if inv else 0
                if item['quantity'] > available:
                    shortages.append(f"{unit.product.display_name} ({unit.name}): متاح {available} فقط")

            if shortages:
                for s in shortages:
                    messages.error(request, f'الكمية غير متوفرة — {s}')
                return redirect('orders:cart')

            order = Order.objects.create(
                client=request.user,
                notes=request.POST.get('notes', ''),
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product_unit=item['unit'],
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                )
                inv = locked_inventories[item['unit'].pk]
                StockMovement.objects.create(
                    inventory=inv,
                    movement_type=StockMovement.MovementType.RESERVE,
                    quantity=item['quantity'],
                    note=f'حجز لطلب #{order.pk}',
                    created_by=request.user,
                )
        cart.clear()
        messages.success(request, f'تم إرسال طلبك رقم #{order.pk} بنجاح!')
        return redirect('orders:order_detail', pk=order.pk)

    return render(request, 'orders/checkout.html', {
        'cart_items': items,
        'total': cart.get_total(),
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, client=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_list(request):
    if request.user.role != 'CLIENT':
        return redirect('catalog:home')
    orders = Order.objects.filter(client=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_approve_amendment(request, pk):
    order = get_object_or_404(Order, pk=pk, client=request.user)
    if order.status != Order.Status.NEEDS_APPROVAL:
        messages.error(request, 'الطلب ده مش بانتظار موافقتك.')
        return redirect('orders:order_detail', pk=order.pk)
    order.client_approve_amendment(actor=request.user)
    messages.success(request, f'تمت الموافقة على التعديل، الطلب #{order.pk} مؤكد دلوقتي.')
    return redirect('orders:order_detail', pk=order.pk)


@login_required
def order_reject_amendment(request, pk):
    order = get_object_or_404(Order, pk=pk, client=request.user)
    if order.status != Order.Status.NEEDS_APPROVAL:
        messages.error(request, 'الطلب ده مش بانتظار موافقتك.')
        return redirect('orders:order_detail', pk=order.pk)
    order.client_reject_amendment(actor=request.user)
    messages.success(request, f'تم رفض التعديل، الطلب #{order.pk} اترفض.')
    return redirect('orders:order_detail', pk=order.pk)
