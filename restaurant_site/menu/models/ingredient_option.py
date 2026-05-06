from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class IngredientOption(models.Model):
    group = models.ForeignKey(
        'menu.IngredientGroup',
        on_delete=models.CASCADE,
        related_name='options'
    )

    ingredient = models.ForeignKey('menu.Ingredient', on_delete=models.CASCADE)
    price_delta = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ingredient} ({self.group})"