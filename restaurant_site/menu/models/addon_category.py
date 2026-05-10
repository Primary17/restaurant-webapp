from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class AddonCategory(MPTTModel):
    name = models.CharField(max_length=100)

    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    def __str__(self):
        return self.name