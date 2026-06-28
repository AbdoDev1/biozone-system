from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'مدير'
        WAREHOUSE = 'WAREHOUSE', 'مخزن'
        CLIENT = 'CLIENT', 'عميل'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
    )

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'في الانتظار'
        ACTIVE = 'ACTIVE', 'نشط'
        REJECTED = 'REJECTED', 'مرفوض'

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class ClientProfile(models.Model):
    class BusinessType(models.TextChoices):
        PHARMACY = 'PHARMACY', 'صيدلية'
        HOSPITAL = 'HOSPITAL', 'مستشفى'
        CLINIC = 'CLINIC', 'عيادة'
        OTHER = 'OTHER', 'أخرى'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='client_profile',
    )
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(
        max_length=20,
        choices=BusinessType.choices,
    )
    address = models.TextField()
    phone = models.CharField(max_length=20)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.business_name} - {self.user.username}"
