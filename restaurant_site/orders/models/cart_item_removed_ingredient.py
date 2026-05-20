from django.db import models

class CartItemRemovedIngredient(models.Model):
    item = models.ForeignKey('orders.CartItem', on_delete=models.CASCADE, related_name='removed_ingredients')
    ingredient = models.ForeignKey('menu.Ingredient', on_delete=models.CASCADE)

    def __str__(self):
        return f"Remove {self.ingredient.name} from {self.item.dish.name}"