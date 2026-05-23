from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('menu/', views.menu, name='menu'),
    path('menu/<int:dish_id>/', views.dish_detail, name='dish_detail'),
    path('menu/ajax/', views.menu_ajax, name='menu_ajax'),
    path('checkout/', views.checkout, name='checkout'),
]