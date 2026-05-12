from rest_framework import generics
from rest_framework.permissions import AllowAny

from menu.models import Category, Dish

from .serializers import (
    CategoryTreeSerializer,
    DishDetailSerializer,
    DishListSerializer,
)


class CategoryTreeView(generics.ListAPIView):
    """Корені дерева категорій меню (MPTT); у кожного вузла рекурсивно вкладені children."""

    permission_classes = [AllowAny]
    serializer_class = CategoryTreeSerializer

    def get_queryset(self):
        return Category.objects.filter(parent=None).order_by('tree_id', 'lft')


class DishListView(generics.ListAPIView):
    """
    Каталог страв. Підтримані query-параметри (база для подальших фільтрів):
    - category — id категорії;
    - search — підрядок у назві (без урахування регістру);
    - ordering — name, -name, base_price, -base_price, id, -id.
    """

    permission_classes = [AllowAny]
    serializer_class = DishListSerializer

    def get_queryset(self):
        qs = (
            Dish.objects.filter(is_active=True)
            .select_related('category')
            .prefetch_related('images')
        )
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)
        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(name__icontains=search)
        ordering = self.request.query_params.get('ordering', 'name')
        allowed = {'name', '-name', 'base_price', '-base_price', 'id', '-id'}
        if ordering in allowed:
            qs = qs.order_by(ordering)
        else:
            qs = qs.order_by('name')
        return qs


class DishDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = DishDetailSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return (
            Dish.objects.filter(is_active=True)
            .select_related('category')
            .prefetch_related(
                'images',
                'addon_groups__category',
                'ingredient_groups__options__ingredient',
            )
        )
