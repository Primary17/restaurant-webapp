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
            ('lactose_free', 'Без лактози'),
            ('nut_free', 'Без горіхів')
        ],
        method="filter_by_diet"
    )

    ingredients_any = django_filters.BaseInFilter(method="filter_by_ingredients_any", distinct=True)
    categories_any = django_filters.BaseInFilter(method="filter_by_categories_any", distinct=True)
    diets_any = django_filters.BaseInFilter(method="filter_by_diets_any", distinct=True)

    class Meta:
        model = Dish
        fields = [
            "category", "categories_any", 
            "is_active", "search", "ordering", 
            "ingredients", "ingredients_any", 
            "diet", "diets_any"
        ]

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
    
    def filter_by_categories_any(self, queryset, name, value):
        """
        Приймає список ID категорій через кому й повертає страви,
        які належать хоча б до однієї з них або їхніх нащадків.
        """
        if not value:
            return queryset
        
        full_categories_pool = Category.objects.none()
        for cat_id in value:
            try:
                category = Category.objects.get(id=cat_id)
                full_categories_pool |= category.get_descendants(include_self=True)
            except Category.DoesNotExist:
                continue
                
        return queryset.filter(category__in=full_categories_pool).distinct()
    
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
    
    def filter_by_ingredients_any(self, queryset, name, value):
        """
        Фільтрує страви за принципом OR: страва повинна містити
        хоча б один інгредієнт із переданого списку `value`.
        """
        if not value:
            return queryset

        return queryset.filter(
            ingredient_groups__options__ingredient__id__in=value
        ).distinct()
    
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
    
    def filter_by_diets_any(self, queryset, name, value):
        """
        Приймає список дієт через кому (наприклад: vegan,lactose_free)
        і повертає страви, які відповідають ХОЧА Б ОДНІЙ із цих дієт.
        """
        if not value:
            return queryset

        query_filter = Q()
        for diet_slug in value:
            if diet_slug == 'vegan':
                query_filter |= Q(is_vegan=True)
            elif diet_slug == 'vegetarian':
                query_filter |= Q(is_vegetarian=True)
            elif diet_slug == 'gluten_free':
                query_filter |= Q(is_gluten_free=True)
            elif diet_slug == 'lactose_free':
                query_filter |= Q(is_lactose_free=True)
            elif diet_slug == 'nut_free':
                query_filter |= Q(is_nut_free=True)

        return queryset.filter(query_filter).distinct()