from django.db import models

# Create your models here.
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


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        IN = 'IN', 'وارد'
        OUT = 'OUT', 'صادر'
        RESERVE = 'RESERVE', 'حجز'
        RELEASE = 'RELEASE', 'إلغاء حجز'

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='movements',
    )
    movement_type = models.CharField(
        max_length=10,
        choices=MovementType.choices,
    )
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
        return f"{self.get_movement_type_display()} — {self.quantity} — {self.inventory.product_unit}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        inv = self.inventory
        if self.movement_type == self.MovementType.IN:
            inv.quantity += self.quantity
        elif self.movement_type == self.MovementType.OUT:
            inv.quantity -= self.quantity
        elif self.movement_type == self.MovementType.RESERVE:
            inv.reserved += self.quantity
        elif self.movement_type == self.MovementType.RELEASE:
            inv.reserved -= self.quantity
        inv.save()
