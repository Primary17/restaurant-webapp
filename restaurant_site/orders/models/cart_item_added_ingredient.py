from django.db import models

class CartItemAddedIngredient(models.Model):
    item = models.ForeignKey('orders.CartItem', on_delete=models.CASCADE, related_name='added_ingredients')
    ingredient = models.ForeignKey('menu.Ingredient', on_delete=models.CASCADE)

    def __str__(self):
        return f"Add {self.ingredient.name} to {self.item.dish.name}"