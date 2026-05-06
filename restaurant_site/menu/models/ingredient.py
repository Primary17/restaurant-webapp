from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='ingredients/', null=True, blank=True)

    def __str__(self):
        return self.name