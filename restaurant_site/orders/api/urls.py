from django.urls import path
from .views import (
    CreateOrderView,
    MyOrdersView,
    OrderDetailView,
    UpdateStatusView
)
from .cart_views import CartView, AddToCartView

urlpatterns = [
    path('', CreateOrderView.as_view()),
    path('my/', MyOrdersView.as_view()),
    path('<int:pk>/', OrderDetailView.as_view()),
    path('<int:pk>/status/', UpdateStatusView.as_view()),
]