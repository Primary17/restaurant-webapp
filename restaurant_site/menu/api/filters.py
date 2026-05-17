import django_filters
from django.db.models import Count, Q
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

    diet = django_filters.ChoiceFilter(
        choices=[
            ('vegan', 'Веганське'),
            ('vegetarian', 'Вегетаріанське'),
            ('gluten_free', 'Без глютену'),
            ('lactose_free', 'Без лактози'),  # <-- ДОДАЛИ
            ('nut_free', 'Без горіхів')
        ],
        method="filter_by_diet"
    )

    class Meta:
        model = Dish
        fields = ["category", "is_active", "search", "ordering", "ingredients", "diet"]

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
    
    def filter_by_diet(self, queryset, name, value):
        if not value:
            return queryset

        if value == 'vegan':
            return queryset.filter(is_vegan=True)
        elif value == 'vegetarian':
            return queryset.filter(is_vegetarian=True)
        elif value == 'gluten_free':
            return queryset.filter(is_gluten_free=True)
        elif value == 'lactose_free':
            return queryset.filter(is_lactose_free=True)
        elif value == 'nut_free':
            return queryset.filter(is_nut_free=True)

        return queryset