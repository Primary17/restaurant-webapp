from django.db import models


class CartItemIngredient(models.Model):
    item = models.ForeignKey('orders.CartItem', on_delete=models.CASCADE, related_name='ingredients')
    ingredient_option = models.ForeignKey('menu.IngredientOption', on_delete=models.CASCADE)