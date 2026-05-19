"""
Валідація вибору додатків і інгредієнтів для страви.
Розширена комбінована фільтрація й кастомізація можуть бути додані окремо;
тут — базові правила за DishAddonGroup та IngredientGroup.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from menu.models import Addon, DishAddonGroup, IngredientGroup, IngredientOption, Ingredient


def _addon_category_ids_under(root) -> list[int]:
    """Усі категорії додатків у піддереві MPTT (включно з root)."""
    return list(root.get_descendants(include_self=True).values_list("pk", flat=True))


def validate_addons_for_dish(dish, selected_addon_ids: Iterable[int]) -> None:
    """Перевіряє, що додатки дозволені для страви й відповідають правилам груп."""
    selected_addon_ids = list(selected_addon_ids or [])
    if len(selected_addon_ids) != len(set(selected_addon_ids)):
        raise ValueError("Дублікати ідентифікаторів додатків у одному рядку")

    groups = list(
        DishAddonGroup.objects.filter(dish=dish).select_related("category")
    )
    allowed_category_ids: set[int] = set()
    for g in groups:
        allowed_category_ids.update(_addon_category_ids_under(g.category))

    addons = list(Addon.objects.filter(pk__in=selected_addon_ids).select_related("category"))
    found_ids = {a.pk for a in addons}
    missing = set(selected_addon_ids) - found_ids
    if missing:
        missing_labels = [f"[ID: {uid}]" for uid in sorted(missing)]
        raise ValueError("Невідомі додатки: %s" % ", ".join(missing_labels))

    for addon in addons:
        if addon.category_id not in allowed_category_ids:
            raise ValueError("Додаток «%s» недоступний для цієї страви" % addon.name)

    by_group: dict[int, list[Addon]] = defaultdict(list)
    for g in groups:
        cat_ids = set(_addon_category_ids_under(g.category))
        for addon in addons:
            if addon.category_id in cat_ids:
                by_group[g.pk].append(addon)

    for g in groups:
        chosen = by_group.get(g.pk, [])
        if g.is_required and not chosen:
            raise ValueError(
                "Обов'язковий вибір у групі додатків «%s»" % g.category.name
            )
        if len(chosen) > g.max_choices:
            raise ValueError(
                "У групі «%s» обрано забагато додатків (макс. %s)"
                % (g.category.name, g.max_choices)
            )


def validate_ingredient_options_for_dish(dish, selected_option_ids: Iterable[int]) -> None:
    """Перевіряє опції інгредієнтів для IngredientGroup (обов'язковість, max_choices)."""
    selected_option_ids = list(selected_option_ids or [])
    if len(selected_option_ids) != len(set(selected_option_ids)):
        raise ValueError("Дублікати опцій інгредієнтів у одному рядку")

    groups = list(IngredientGroup.objects.filter(dish=dish))
    if not groups and selected_option_ids:
        raise ValueError("Для цієї страви немає груп інгредієнтів")

    options = list(
        IngredientOption.objects.filter(
            pk__in=selected_option_ids, group__dish=dish
        ).select_related("group")
    )
    found = {o.pk for o in options}
    missing = set(selected_option_ids) - found
    if missing:
        missing_labels = [f"[ID: {uid}]" for uid in sorted(missing)]
        raise ValueError("Невідомі опції інгредієнтів: %s" % ", ".join(missing_labels))

    by_group: dict[int, list[IngredientOption]] = defaultdict(list)
    for opt in options:
        by_group[opt.group_id].append(opt)

    for g in groups:
        n = len(by_group.get(g.pk, []))
        if g.is_required and n < 1:
            raise ValueError("Обов'язковий вибір у групі «%s»" % g.name)
        if n > g.max_choices:
            raise ValueError(
                "У групі «%s» обрано забагато варіантів (макс. %s)"
                % (g.name, g.max_choices)
            )


def validate_removed_ingredients(dish, removed_ingredient_ids: Iterable[int]) -> None:
    """Перевіряє, що інгредієнти, які вилучаються, дійсно є у складі цієї страви."""
    removed_ingredient_ids = list(removed_ingredient_ids or [])
    if not removed_ingredient_ids:
        return

    if len(removed_ingredient_ids) != len(set(removed_ingredient_ids)):
        raise ValueError("Дублікати ідентифікаторів у списку вилучених інгредієнтів")

    allowed_ingredient_ids = set(
        Ingredient.objects.filter(
            ingredientoption__group__dish=dish
        ).values_list('id', flat=True)
    )

    missing = set(removed_ingredient_ids) - allowed_ingredient_ids
    if missing:
        invalid_ingredients = Ingredient.objects.filter(pk__in=missing)
        
        invalid_names = []
        for uid in sorted(missing):
            ing_obj = next((i for i in invalid_ingredients if i.pk == uid), None)
            if ing_obj:
                invalid_names.append(f"«{ing_obj.name}»")
            else:
                invalid_names.append(f"[Невідомий інгредієнт ID: {uid}]")

        raise ValueError(
            "Неможливо видалити інгредієнти %s, оскільки вони не входять до складу страви" 
            % ", ".join(invalid_names)
        )
    

def validate_order_line(
    dish, 
    addon_ids: Iterable[int], 
    ingredient_option_ids: Iterable[int],
    removed_ingredient_ids: Iterable[int] = None,
    added_ingredient_ids: Iterable[int] = None
) -> None:
    """Повна перевірка одного рядка замовлення / кошика з урахуванням кастомних соусів."""
    # Об'єднуємо звичайні аддони та кастомні додатки в один список для перевірки категорій
    all_addons = list(addon_ids or []) + list(added_ingredient_ids or [])
    
    validate_addons_for_dish(dish, all_addons)
    validate_ingredient_options_for_dish(dish, ingredient_option_ids)
    validate_removed_ingredients(dish, removed_ingredient_ids)

