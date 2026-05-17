from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Dish(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey('menu.Category', on_delete=models.PROTECT)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)

    is_active = models.BooleanField(default=True)

    is_vegan = models.BooleanField(default=True, db_index=True)
    is_vegetarian = models.BooleanField(default=True, db_index=True)
    is_gluten_free = models.BooleanField(default=True, db_index=True)
    is_lactose_free = models.BooleanField(default=True, db_index=True)
    is_nut_free = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['category', 'is_active'], name='dish_category_active_idx'),
        ]

    def __str__(self):
        return self.name
    
    def recalculate_diets(self):
        from menu.models.ingredient_option import IngredientOption
        
        options = IngredientOption.objects.filter(group__dish=self).select_related('ingredient')
        
        if not options.exists():
            self.is_vegan = True
            self.is_vegetarian = True
            self.is_gluten_free = True
            self.is_lactose_free = True
            self.is_nut_free = True
        else:
            self.is_vegan = not options.filter(ingredient__is_vegan=False).exists()
            self.is_vegetarian = not options.filter(ingredient__is_vegetarian=False).exists()
            self.is_gluten_free = not options.filter(ingredient__is_gluten_free=False).exists()
            self.is_lactose_free = not options.filter(ingredient__is_lactose_free=False).exists()
            self.is_nut_free = not options.filter(ingredient__is_nut_free=False).exists()
        
        # Швидкий апдейт в один запит
        Dish.objects.filter(pk=self.pk).update(
            is_vegan=self.is_vegan,
            is_vegetarian=self.is_vegetarian,
            is_gluten_free=self.is_gluten_free,
            is_lactose_free=self.is_lactose_free,
            is_nut_free=self.is_nut_free
        )


class DishImage(models.Model):
    dish = models.ForeignKey('menu.Dish', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='dishes/')
    is_main = models.BooleanField(default=False)