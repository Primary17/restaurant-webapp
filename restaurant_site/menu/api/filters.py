import django_filters
# Імпортуємо моделі безпосередньо з файлів, де вони створені
from menu.models.dish import Dish
from menu.models.category import Category


class DishFilter(django_filters.FilterSet):
    # Фільтр категорій MPTT
    category = django_filters.NumberFilter(method="filter_by_category_tree")

    # Пошук за підрядком у назві страви
    search = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains"
    )

    # Сортування
    ordering = django_filters.OrderingFilter(
        fields=(
            ("name", "name"),
            ("base_price", "base_price"),
            ("id", "id"),
        )
    )

    class Meta:
        model = Dish
        fields = ["category", "is_active", "search", "ordering"]

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