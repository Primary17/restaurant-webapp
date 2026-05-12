from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from orders.models import Order
from .serializers import OrderSerializer, CreateOrderSerializer
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


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = Order.objects.get(pk=pk)

        if order.user != request.user and request.user.role not in ['staff', 'admin']:
            return Response(status=403)

        return Response(OrderSerializer(order).data)


class UpdateStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        order = Order.objects.get(pk=pk)

        if request.user.role not in ['staff', 'admin']:
            return Response(status=403)

        order.status = request.data.get('status', order.status)
        order.save()

        return Response({"status": order.status})