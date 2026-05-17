from django.db import models

class OrderItemRemovedIngredient(models.Model):
    item = models.ForeignKey('orders.OrderItem', on_delete=models.CASCADE, related_name='removed_ingredients')
    ingredient = models.ForeignKey('menu.Ingredient', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100) 

    def __str__(self):
        return f"Removed: {self.name}"