from django.urls import path

from .cart_views import (
    AddToCartView,
    CartItemDetailView,
    CartView,
    CheckoutView,
)
from .views import (
    CreateOrderView,
    MyOrdersView,
    OrderDetailView,
    StaffOrdersView,
    UpdateStatusView,
)

urlpatterns = [
    path('cart/', CartView.as_view()),
    path('cart/items/', AddToCartView.as_view()),
    path('cart/items/<int:pk>/', CartItemDetailView.as_view()),
    path('cart/checkout/', CheckoutView.as_view()),
    path('my/', MyOrdersView.as_view()),
    path('staff/', StaffOrdersView.as_view()),
    path('<int:pk>/status/', UpdateStatusView.as_view()),
    path('<int:pk>/', OrderDetailView.as_view()),
    path('', CreateOrderView.as_view()),
]
