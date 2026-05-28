from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CUSTOMER = 'customer'
    ROLE_STAFF = 'staff'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = (
        (ROLE_CUSTOMER, 'Customer'),
        (ROLE_STAFF, 'Staff'),
        (ROLE_ADMIN, 'Admin'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CUSTOMER,
        verbose_name='Role on site',
        help_text=(
            'Customer — only orders. Staff and Admin — orders panel. '
            'Access to this Django-admin is synchronized with role automatically.'
        ),
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Phone')

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.username

    def sync_staff_flag_from_role(self):
        """is_staff = access to Django-admin; synchronized with role (except superuser)."""
        if self.is_superuser:
            return
        self.is_staff = self.role in (self.ROLE_STAFF, self.ROLE_ADMIN)

    def save(self, *args, **kwargs):
        self.sync_staff_flag_from_role()
        super().save(*args, **kwargs)