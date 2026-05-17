from rest_framework import generics
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from menu.models.dish import Dish
from menu.api.filters import DishFilter

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
    Каталог страв із підтримкою ієрархічної фільтрації за категоріями (MPTT).
    """

    permission_classes = [AllowAny]
    serializer_class = DishListSerializer

    # Підключаємо систему фільтрації DjangoFilterBackend
    filter_backends = [DjangoFilterBackend]
    filterset_class = DishFilter

    def get_queryset(self):
        # Повертаємо чистий оптимізований запит БЕЗ ручних фільтрацій за query_params
        return (
            Dish.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("images")
            .order_by("name")
        )

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
