from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from menu.models.ingredient_option import IngredientOption
from menu.models.ingredient import Ingredient
from menu.models.dish import Dish


@receiver([post_save, post_delete], sender=IngredientOption)
def handle_ingredient_option_change(sender, instance, **kwargs):
    """
    Сигнал спрацьовує, коли страві додають, змінюють або видаляють інгредієнт.
    """
    if instance.group and instance.group.dish:
        instance.group.dish.recalculate_diets()


@receiver(post_save, sender=Ingredient)
def handle_ingredient_field_change(sender, instance, **kwargs):
    """
    Сигнал спрацьовує, якщо ти змінюєш прапорці у самому інгредієнті
    (наприклад, змінила 'Томати' з is_vegan=False на True).
    Він перерахує статус для ВСІХ страв, де є цей інгредієнт.
    """
    dishes = Dish.objects.filter(ingredient_groups__options__ingredient=instance).distinct()
    for dish in dishes:
        dish.recalculate_diets()