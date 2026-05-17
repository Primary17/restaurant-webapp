import django_filters
from django.db.models import Count
from menu.models.dish import Dish
from menu.models.category import Category


class DishFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(method="filter_by_category_tree")
    search = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains"
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("name", "name"),
            ("base_price", "base_price"),
            ("id", "id"),
        )
    )

    ingredients = django_filters.BaseInFilter(
        method="filter_by_ingredients", distinct=True
    )

    class Meta:
        model = Dish
        fields = ["category", "is_active", "search", "ordering", "ingredients"]

    def filter_by_category_tree(self, queryset, name, value):
        """
        Приймає ID категорії, знаходить усіх її нащадків у дереві MPTT
        і повертає страви, які належать будь-якій із цих підкатегорій.
        """
        if not value:
            return queryset
        try:
            category = Category.objects.get(id=value)
            categories = category.get_descendants(include_self=True)
            return queryset.filter(category__in=categories)
        except Category.DoesNotExist:
            return queryset.none()

    def filter_by_ingredients(self, queryset, name, value):
        """
        Фільтрує страви за принципом AND: страва повинна містити
        абсолютно кожен інгредієнт із переданого списку `value`.
        """
        if not value:
            return queryset

        # Кількість унікальних інгредієнтів, які шукає користувач
        num_ingredients = len(set(value))

        # Шукаємо страви, у яких є збіги з цими інгредієнтами,
        # групуємо за ID страви і залишаємо тільки ті страви,
        # де кількість збігів дорівнює кількості шуканих інгредієнтів.
        matched_dishes = (
            queryset.filter(
                ingredient_groups__options__ingredient__id__in=value
            )
            .annotate(
                matching_count=Count(
                    "ingredient_groups__options__ingredient", distinct=True
                )
            )
            .filter(matching_count=num_ingredients)
        )

        return matched_dishes