from django.db import models
from decimal import Decimal


class CartItem(models.Model):
    cart = models.ForeignKey('orders.Cart', on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey('menu.Dish', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.dish.name} x {self.quantity} in Cart"

    @property
    def price_per_unit(self):
        """
        Обчислює вартість однієї одиниці страви з урахуванням усіх 
        кастомізованих опцій інгредієнтів та додатків.
        """
        # Базова ціна страви
        price = self.dish.base_price
        
        # Додаємо дельти цін усіх обраних інгредієнтів
        for item_ingredient in self.ingredients.all():
            price += item_ingredient.ingredient_option.price_delta
            
        # Додаємо ціни всіх обраних додатків
        for item_addon in self.addons.all():
            price += item_addon.addon.price
            
        return price

    @property
    def total_price(self):
        """
        Повертает загальну вартість цієї позиції в кошику (ціна за одиницю * кількість).
        """
        return self.price_per_unit * self.quantity