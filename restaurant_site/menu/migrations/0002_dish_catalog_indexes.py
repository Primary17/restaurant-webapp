# Generated manually for catalog / filter queries on active dishes by category.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='dish',
            index=models.Index(
                fields=['category', 'is_active'],
                name='dish_category_active_idx',
            ),
        ),
    ]
