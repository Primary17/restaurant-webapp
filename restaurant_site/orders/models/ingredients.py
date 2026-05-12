from django.db import models


class OrderItemIngredient(models.Model):
    item = models.ForeignKey(
        'orders.OrderItem',
        on_delete=models.CASCADE,
        related_name='ingredients'
    )

    ingredient = models.ForeignKey(
        'menu.Ingredient',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    price_delta = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name