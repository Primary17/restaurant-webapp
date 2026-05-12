from django.core.exceptions import ValidationError
from django.db import models


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

    def clean(self):
        if self.max_choices < 1:
            raise ValidationError("max_choices must be >= 1")