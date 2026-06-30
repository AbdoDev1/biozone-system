from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User
from products.models import ProductUnit


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
