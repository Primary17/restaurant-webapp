from django.db import models
from decimal import Decimal


class Cart(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart ({self.user})"

    @property
    def total_price(self):
        """
        Обчислює сумарну вартість усіх кастомізованих позицій у кошику.
        """
        # Використовуємо sum() по наших property з CartItem. 
        # За замовчуванням повертаємо Decimal('0.00'), якщо кошик порожній.
        return sum((item.total_price for item in self.items.all()), Decimal('0.00'))