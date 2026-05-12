from django.urls import path

from .views import CategoryTreeView, DishDetailView, DishListView

urlpatterns = [
    path('categories/', CategoryTreeView.as_view(), name='menu-categories'),
    path('dishes/', DishListView.as_view(), name='menu-dishes'),
    path('dishes/<int:pk>/', DishDetailView.as_view(), name='menu-dish-detail'),
]
