from django.db import models


class CartItem(models.Model):
    cart = models.ForeignKey('orders.Cart', on_delete=models.CASCADE, related_name='items')

    dish = models.ForeignKey('menu.Dish', on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)