from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from orders.models import Order, OrderItem


def _staff_required(user):
    return user.is_authenticated and user.role in ['ADMIN', 'WAREHOUSE']


@login_required
def order_list(request):
    if not _staff_required(request.user):
        return redirect('catalog:home')

    status = request.GET.get('status', '')
    orders = Order.objects.select_related('client').prefetch_related('items')

    if status:
        orders = orders.filter(status=status)

    context = {
        'orders': orders,
        'selected_status': status,
        'status_choices': Order.Status.choices,
    }
    return render(request, 'staff/orders/list.html', context)


@login_required
def order_detail(request, pk):
    if not _staff_required(request.user):
        return redirect('catalog:home')

    order = get_object_or_404(
        Order.objects.select_related('client').prefetch_related('items__product_unit__inventory'),
        pk=pk,
    )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_quantities':
            any_changed = False
            for item in order.items.all():
                field_name = f'quantity_{item.pk}'
                if field_name not in request.POST:
                    continue
                try:
                    new_qty = int(request.POST.get(field_name))
                except (TypeError, ValueError):
                    continue
                if new_qty == item.quantity or new_qty < 0:
                    continue
                if new_qty == 0:
                    messages.error(request, 'مينفعش تصفّر كمية صنف من هنا، استخدم رفض الطلب لو محتاج تشيله بالكامل.')
                    continue
                try:
                    order.amend_item_quantity(item, new_qty, actor=request.user)
                    any_changed = True
                except ValueError as e:
                    messages.error(request, str(e))

            if any_changed:
                order.send_for_client_approval(actor=request.user)
                messages.success(request, 'تم تعديل الكميات وإرسال الطلب للعميل للموافقة على التعديل.')
            else:
                messages.info(request, 'مفيش تعديلات تم تطبيقها.')
            return redirect('staff:order_detail', pk=order.pk)

        elif action == 'confirm':
            if order.is_amended and order.status != Order.Status.NEEDS_APPROVAL:
                messages.error(request, 'الطلب فيه تعديلات لسه محتاجة موافقة العميل، مينفعش تأكده مباشرة.')
            else:
                order.confirm(actor=request.user)
                messages.success(request, f'تم تأكيد الطلب #{order.pk}.')
            return redirect('staff:order_detail', pk=order.pk)

        elif action == 'reject':
            reason = request.POST.get('reason', '')
            order.reject(actor=request.user, reason=reason)
            messages.success(request, f'تم رفض الطلب #{order.pk} وفك الحجز.')
            return redirect('staff:order_detail', pk=order.pk)

        elif action == 'deliver':
            if order.status != Order.Status.CONFIRMED:
                messages.error(request, 'لازم الطلب يكون مؤكد الأول قبل التسليم.')
            else:
                order.mark_delivered(actor=request.user)
                messages.success(request, f'تم تسليم الطلب #{order.pk}.')
            return redirect('staff:order_detail', pk=order.pk)

    return render(request, 'staff/orders/detail.html', {'order': order})
