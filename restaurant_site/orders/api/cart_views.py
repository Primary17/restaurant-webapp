from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Cart, CartItem
from menu.models import Dish


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)

        return Response({
            "items": [
                {
                    "id": item.id,
                    "dish": item.dish.name,
                    "quantity": item.quantity
                }
                for item in cart.items.all()
            ]
        })


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)

        dish = Dish.objects.get(id=request.data['dish_id'])

        item = CartItem.objects.create(
            cart=cart,
            dish=dish,
            quantity=request.data.get('quantity', 1)
        )

        return Response({"id": item.id})