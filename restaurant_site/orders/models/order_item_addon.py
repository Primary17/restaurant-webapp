from django.db import models


class OrderItemAddon(models.Model):
    item = models.ForeignKey(
        'orders.OrderItem',
        on_delete=models.CASCADE,
        related_name='addons'
    )

    addon = models.ForeignKey(
        'menu.Addon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name