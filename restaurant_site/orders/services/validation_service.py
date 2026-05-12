from menu.models import DishAddongroup, IngredientGroup


def validate_addons(dish, selected_addons):
    groups = Dishaddongroup.objects.filter(dish=dish)

    for group in groups:
        addons_in_group = [
            a for a in selected_addons
            if a.category_id == group.category_id
        ]

        if group.is_required and not addons_in_group:
            raise ValueError("Required addon missing")

        if len(addons_in_group) > group.max_choices:
            raise ValueError("Too many addons selected")