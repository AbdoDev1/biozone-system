from django.db import models
from products.models import ProductUnit


class Inventory(models.Model):
    product_unit = models.OneToOneField(
        ProductUnit,
        on_delete=models.CASCADE,
        related_name='inventory',
    )
    quantity = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    min_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(
        default=True,
        verbose_name='متوفر في الكتالوج',
        help_text='يتم تحديثه تلقائياً عند انخفاض الكمية، أو يمكن التحكم فيه يدوياً'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'مخزون'
        verbose_name_plural = 'المخزون'

    def __str__(self):
        return f"{self.product_unit} — {self.quantity}"

    @property
    def available(self):
        return self.quantity - self.reserved

    @property
    def is_low(self):
        return self.available <= self.min_quantity

    def sync_availability(self):
        if self.available <= 0:
            self.is_available = False
        elif self.is_low and self.min_quantity > 0:
            self.is_available = False
        else:
            self.is_available = True
        self.save(update_fields=['is_available'])


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        IN = 'IN', 'وارد'
        OUT = 'OUT', 'صادر (مباشر)'
        OUT_RESERVED = 'OUT_RESERVED', 'صادر (من محجوز عند التسليم)'
        RESERVE = 'RESERVE', 'حجز'
        RELEASE = 'RELEASE', 'إلغاء حجز'

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='movements',
    )
    movement_type = models.CharField(max_length=13, choices=MovementType.choices)
    quantity = models.PositiveIntegerField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'حركة مخزون'
        verbose_name_plural = 'حركات المخزون'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.inventory.product_unit.product.display_name}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.quantity is None or self.quantity <= 0:
            raise ValidationError('الكمية يجب أن تكون أكبر من صفر.')
        if self.inventory_id:
            if self.movement_type == self.MovementType.OUT and self.quantity > self.inventory.available:
                raise ValidationError(
                    'الكمية المطلوبة أكبر من الكمية المتاحة (غير المحجوزة) في المخزون.'
                )
            if self.movement_type == self.MovementType.OUT_RESERVED and self.quantity > self.inventory.reserved:
                raise ValidationError(
                    'الكمية المطلوب تسليمها أكبر من الكمية المحجوزة فعليًا لهذا الطلب.'
                )
            if self.movement_type == self.MovementType.RELEASE and self.quantity > self.inventory.reserved:
                raise ValidationError('لا يمكن إلغاء حجز أكبر من الكمية المحجوزة فعليًا.')

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if not is_new:
            return
        from django.db.models import F
        inv_qs = Inventory.objects.filter(pk=self.inventory_id)
        if self.movement_type == self.MovementType.IN:
            inv_qs.update(quantity=F('quantity') + self.quantity)
        elif self.movement_type in (self.MovementType.OUT, self.MovementType.OUT_RESERVED):
            inv_qs.update(quantity=F('quantity') - self.quantity)
        elif self.movement_type == self.MovementType.RESERVE:
            inv_qs.update(reserved=F('reserved') + self.quantity)
        elif self.movement_type == self.MovementType.RELEASE:
            inv_qs.update(reserved=F('reserved') - self.quantity)
        self.inventory.refresh_from_db()
        self.inventory.sync_availability()
