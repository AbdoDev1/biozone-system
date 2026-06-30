from django.db import models
from accounts.models import User
from products.models import ProductUnit


class SiteConfig(models.Model):
    """
    إعدادات عامة للموقع — سطر واحد بس (Singleton).
    يتم التعديل عليه من لوحة الأدمن.
    """
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='الحد الأدنى لقيمة الطلب',
        help_text='أقل قيمة إجمالية مسموح بها لإرسال الطلب (بالجنيه). اتركها صفر لو مش عايز حد أدنى.',
    )

    class Meta:
        verbose_name = 'إعدادات الموقع'
        verbose_name_plural = 'إعدادات الموقع'

    def __str__(self):
        return 'إعدادات الموقع'

    def save(self, *args, **kwargs):
        # نضمن وجود سطر واحد بس دايمًا (pk=1)
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # منمنع حذف السطر الوحيد
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING   = 'PENDING',   'في الانتظار'
        CONFIRMED = 'CONFIRMED', 'مؤكد'
        REJECTED  = 'REJECTED',  'مرفوض'
        DELIVERED = 'DELIVERED', 'تم التسليم'

    client      = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    status      = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'
        ordering = ['-created_at']

    def __str__(self):
        return f'طلب #{self.pk} — {self.client.username}'

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_status = self.status

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        status_changed = (not is_new) and (self.status != self._old_status)
        super().save(*args, **kwargs)

        if is_new:
            OrderLog.objects.create(
                order=self,
                event=OrderLog.Event.CREATED,
                note='تم إنشاء الطلب.',
            )
        elif status_changed:
            OrderLog.objects.create(
                order=self,
                event=OrderLog.Event.STATUS_CHANGED,
                note=f'تم تغيير حالة الطلب إلى "{self.get_status_display()}".',
                new_status=self.status,
            )
        self._old_status = self.status


class OrderItem(models.Model):
    order        = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.PROTECT)
    quantity     = models.PositiveIntegerField()
    unit_price   = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'صنف في الطلب'
        verbose_name_plural = 'أصناف الطلب'

    def __str__(self):
        return f'{self.product_unit.name} x{self.quantity}'

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


class OrderLog(models.Model):
    """
    سجل عمليات الطلب — كل حدث بيحصل على الطلب (إنشاء، تغيير حالة، ملاحظة).
    العميل يشوفه كـ تايم لاين في صفحة تفاصيل الطلب.
    """
    class Event(models.TextChoices):
        CREATED        = 'CREATED',        'تم إنشاء الطلب'
        STATUS_CHANGED = 'STATUS_CHANGED',  'تغيير الحالة'
        NOTE           = 'NOTE',            'ملاحظة'

    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='logs')
    event      = models.CharField(max_length=20, choices=Event.choices)
    new_status = models.CharField(max_length=20, choices=Order.Status.choices, blank=True)
    note       = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='order_logs',
    )

    class Meta:
        verbose_name = 'سجل عملية'
        verbose_name_plural = 'سجل العمليات'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.get_event_display()} — طلب #{self.order_id}'
