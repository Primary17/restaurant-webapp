from django.urls import path
from django.conf import settings
from django.urls import re_path
from django.views.static import serve

from .views import CategoryTreeView, DishDetailView, DishListView

urlpatterns = [
    path('categories/', CategoryTreeView.as_view(), name='menu-categories'),
    path('dishes/', DishListView.as_view(), name='menu-dishes'),
    path('dishes/<int:pk>/', DishDetailView.as_view(), name='menu-dish-detail'),
]

# FOR DEMO ONLY (works on Heroku dyno)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]