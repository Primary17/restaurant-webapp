from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class DishAddonGroup(models.Model):
    dish = models.ForeignKey(
        'menu.Dish',
        on_delete=models.CASCADE,
        related_name='addon_groups'
    )

    category = models.ForeignKey('menu.AddonCategory', on_delete=models.CASCADE)

    is_required = models.BooleanField(default=False)
    max_choices = models.PositiveIntegerField(default=3)

    def __str__(self):
        return f"{self.dish} - {self.category}"