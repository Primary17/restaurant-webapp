from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from menu.models import Dish
from orders.models import Cart, CartItem, CartItemAddon, CartItemIngredient, Order

from orders.models import CartItemRemovedIngredient
from orders.services.cart_services import checkout_cart
from orders.services.validation_service import validate_order_line

from .serializers import (
    AddCartItemSerializer,
    CartItemQuantitySerializer,
    CartItemReadSerializer,
    CheckoutSerializer,
    OrderSerializer,
    CartSerializer,
)


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        serializer = CartSerializer(cart)
        
        return Response(serializer.data)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = AddCartItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        cart, _ = Cart.objects.get_or_create(user=request.user)

        dish = get_object_or_404(Dish, pk=data['dish_id'])
        if not dish.is_active:
            return Response(
                {'detail': 'Ця страва наразі недоступна.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        addon_ids = data.get('addons') or []
        ing_ids = data.get('ingredients') or []
        removed_ing_ids = data.get('removed_ingredients') or []
        added_ing_ids = data.get('added_ingredients') or []

        try:
            validate_order_line(dish, addon_ids, ing_ids, removed_ing_ids, added_ing_ids)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        item = CartItem.objects.create(
            cart=cart,
            dish=dish,
            quantity=data['quantity'],
        )
        for aid in addon_ids:
            CartItemAddon.objects.create(
                item=item,
                addon_id=aid,
            )
        for iid in ing_ids:
            CartItemIngredient.objects.create(
                item=item,
                ingredient_option_id=iid,
            )
            
        for riid in removed_ing_ids:
            CartItemRemovedIngredient.objects.create(
                item=item,
                ingredient_id=riid,
            )

        from orders.models import CartItemAddedIngredient
        for aiid in added_ing_ids:
            CartItemAddedIngredient.objects.create(item=item, ingredient_id=aiid)

        item = (
            CartItem.objects.filter(pk=item.pk)
            .select_related('dish')
            .prefetch_related(
                'addons__addon',
                'ingredients__ingredient_option__ingredient',
                'removed_ingredients__ingredient',
                'added_ingredients__ingredient',
            )
            .first()
        )
        return Response(
            CartItemReadSerializer(item).data,
            status=status.HTTP_201_CREATED,
        )


class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_cart_item(self, request, pk):
        cart = get_object_or_404(Cart, user=request.user)
        return get_object_or_404(
            CartItem.objects.select_related('dish').prefetch_related(
                'addons__addon',
                'ingredients__ingredient_option__ingredient',
                'removed_ingredients__ingredient',
            ),
            pk=pk,
            cart=cart,
        )

    def patch(self, request, pk):
        ser = CartItemQuantitySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        item = self.get_cart_item(request, pk)
        item.quantity = ser.validated_data['quantity']
        item.save(update_fields=['quantity'])
        return Response(CartItemReadSerializer(item).data)

    def delete(self, request, pk):
        item = self.get_cart_item(request, pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = CheckoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            order = checkout_cart(request.user, ser.validated_data)
        except Cart.DoesNotExist:
            return Response(
                {'detail': 'Кошик не знайдено.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        order = (
            Order.objects.filter(pk=order.pk)
            .select_related('user')
            .prefetch_related(
                'items__addons',
                'items__ingredients',
                'items__removed_ingredients', 
                'items__added_ingredients',
            )
            .first()
        )
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )
    