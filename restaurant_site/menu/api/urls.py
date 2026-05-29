from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import CategoryTreeView, DishDetailView, DishListView

urlpatterns = [
    path('categories/', CategoryTreeView.as_view(), name='menu-categories'),
    path('dishes/', DishListView.as_view(), name='menu-dishes'),
    path('dishes/<int:pk>/', DishDetailView.as_view(), name='menu-dish-detail'),
]

if settings.MEDIA_URL:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )