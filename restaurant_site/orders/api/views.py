from django.shortcuts import get_object_or_404
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
        order.save(update_fields=['status', 'updated_at'])

        return Response({"status": order.status})