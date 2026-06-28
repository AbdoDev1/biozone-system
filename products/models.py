from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import FileExtensionValidator

class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='categories/', blank=True, null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])] )
    slug = models.SlugField(unique=True, allow_unicode=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'قسم'
        verbose_name_plural = 'الأقسام'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
    )
    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])] )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'منتج'
        verbose_name_plural = 'المنتجات'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductUnit(models.Model):
    class Size(models.TextChoices):
        SMALL = 'S', 'صغرى'
        MEDIUM = 'M', 'متوسطة'
        LARGE = 'L', 'كبرى'

    class WholesaleMode(models.TextChoices):
        FULL = 'FULL', 'كل الكمية بسعر الجملة'
        TIERED = 'TIERED', 'تدريجي'

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='units',
    )
    size = models.CharField(max_length=1, choices=Size.choices)
    name = models.CharField(max_length=100)
    qty_in_small = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale_min_qty = models.PositiveIntegerField(default=0)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    wholesale_mode = models.CharField(
        max_length=10,
        choices=WholesaleMode.choices,
        default=WholesaleMode.FULL,
    )

    class Meta:
        verbose_name = 'وحدة'
        verbose_name_plural = 'الوحدات'
        unique_together = ('product', 'size')
        ordering = ['size']

    def __str__(self):
        return f"{self.product.name} — {self.name}"

    def get_price(self, qty):
        if self.wholesale_min_qty and qty >= self.wholesale_min_qty and self.wholesale_price:
            if self.wholesale_mode == self.WholesaleMode.FULL:
                return self.wholesale_price * qty
            else:
                return (self.wholesale_price * self.wholesale_min_qty) + \
                       (self.unit_price * (qty - self.wholesale_min_qty))
        return self.unit_price * qty
