from decimal import Decimal
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='ingredients/', null=True, blank=True)

    is_vegan = models.BooleanField(default=True, verbose_name="Веганське")
    is_vegetarian = models.BooleanField(default=True, verbose_name="Вегетаріанське")
    is_gluten_free = models.BooleanField(default=True, verbose_name="Без глютену")
    is_lactose_free = models.BooleanField(default=True, verbose_name="Без лактози")
    is_nut_free = models.BooleanField(default=True, verbose_name="Без горіхів")
    price = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return self.name