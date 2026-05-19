from django.db import models

class OrderItemAddedIngredient(models.Model):
    item = models.ForeignKey('orders.OrderItem', on_delete=models.CASCADE, related_name='added_ingredients')
    ingredient = models.ForeignKey('menu.Ingredient', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name