from django.shortcuts import get_object_or_404
from django.db.models import Sum, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from menu.models import Dish, Addon, IngredientOption, Ingredient
from orders.models import Order, Cart, CartItem
from .serializers import (
    OrderSerializer, 
    CreateOrderSerializer, 
    CartItemReadSerializer, 
    AddCartItemSerializer, 
    CartItemQuantitySerializer,
    CartSerializer
)
from orders.services.order_service import create_order


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = create_order(request.user, serializer.validated_data)

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )


class MyOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user) \
            .select_related('user') \
            .prefetch_related(
                'items__addons',
                'items__ingredients'
            ) \
            .order_by('-created_at')
        return Response(OrderSerializer(orders, many=True).data)


class StaffOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['staff', 'admin']:
            return Response(status=status.HTTP_403_FORBIDDEN)

        status_filter = request.query_params.get('status')
        orders = Order.objects.all()
        if status_filter:
            orders = orders.filter(status=status_filter)

        orders = orders.select_related('user').prefetch_related(
            'items__addons',
            'items__ingredients',
            'items__removed_ingredients',
        ).order_by('-created_at')

        return Response(OrderSerializer(orders, many=True).data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if order.user != request.user and request.user.role not in ['staff', 'admin']:
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(OrderSerializer(order).data)


class UpdateStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if request.user.role not in ['staff', 'admin']:
            return Response(status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get('status')
        if new_status is None:
            return Response(
                {"detail": "Поле status обов'язкове."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        valid = {c[0] for c in Order.STATUS_CHOICES}
        if new_status not in valid:
            return Response(
                {"detail": "Недопустимий статус.", "allowed": sorted(valid)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        items = cart.items.all().select_related('dish').prefetch_related(
            'addons__addon', 
            'ingredients__ingredient_option__group',
            'ingredients__ingredient_option__ingredient',
            'removed_ingredients__ingredient'
        )
        
        serialized_items = CartItemReadSerializer(items, many=True).data
        
        from decimal import Decimal
        cart_total_price = sum(Decimal(str(item['total_price'])) for item in serialized_items)

        return Response({
            "cart_total_price": float(cart_total_price),
            "items": serialized_items
        })

class AddCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart, _ = Cart.objects.get_or_create(user=request.user)
        data = serializer.validated_data
        
        dish = get_object_or_404(Dish, pk=data['dish_id'])
        
        cart_item = CartItem.objects.create(
            cart=cart,
            dish=dish,
            quantity=data['quantity']
        )
        
        for addon_id in data.get('addons', []):
            addon = get_object_or_404(Addon, pk=addon_id)
            cart_item.addons.create(addon=addon)
            
        for option_id in data.get('ingredients', []):
            option = get_object_or_404(IngredientOption, pk=option_id)
            cart_item.ingredients.create(ingredient_option=option)
            
        for removed_id in data.get('removed_ingredients', []):
            ing = get_object_or_404(Ingredient, pk=removed_id)
            cart_item.removed_ingredients.create(ingredient=ing)
            
        return Response(CartItemReadSerializer(cart_item).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        serializer = CartItemQuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart_item.quantity = serializer.validated_data['quantity']
        cart_item.save()
        
        return Response(CartItemReadSerializer(cart_item).data)

    def delete(self, request, pk):
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order = create_order(request.user, serializer.validated_data)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    