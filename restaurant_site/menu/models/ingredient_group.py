from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class IngredientGroup(models.Model):
    dish = models.ForeignKey(
        'menu.Dish',
        on_delete=models.CASCADE,
        related_name='ingredient_groups'
    )

    name = models.CharField(max_length=100)
    is_required = models.BooleanField(default=True)
    max_choices = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.dish} - {self.name}"