from django.db import models


class CartItemAddon(models.Model):
    item = models.ForeignKey('orders.CartItem', on_delete=models.CASCADE, related_name='addons')
    addon = models.ForeignKey('menu.Addon', on_delete=models.CASCADE)