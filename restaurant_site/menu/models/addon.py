from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Addon(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='addons/', null=True, blank=True)
    category = models.ForeignKey('menu.AddonCategory', on_delete=models.PROTECT)

    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name