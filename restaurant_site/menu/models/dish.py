from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Dish(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey('menu.Category', on_delete=models.PROTECT)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class DishImage(models.Model):
    dish = models.ForeignKey('menu.Dish', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='dishes/')
    is_main = models.BooleanField(default=False)