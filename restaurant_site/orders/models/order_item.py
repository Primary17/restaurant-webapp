from django.db import models


class OrderItem(models.Model):
    id = models.BigAutoField(primary_key=True)

    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='items'
    )

    dish = models.ForeignKey(
        'menu.Dish',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=255)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)

    quantity = models.PositiveIntegerField(default=1)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name