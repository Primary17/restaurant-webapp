from rest_framework import serializers
from orders.models import (
    Order,
    OrderItem,
    OrderItemAddon,
    OrderItemIngredient
)


class OrderItemAddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemAddon
        fields = ['id', 'name', 'price']


class OrderItemIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemIngredient
        fields = ['id', 'name', 'price_delta']


class OrderItemSerializer(serializers.ModelSerializer):
    addons = OrderItemAddonSerializer(many=True)
    ingredients = OrderItemIngredientSerializer(many=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'name',
            'base_price',
            'quantity',
            'total_price',
            'addons',
            'ingredients',
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'items_total',
            'delivery_fee',
            'total_price',
            'address',
            'comment',
            'items',
            'created_at'
        ]


class CreateOrderSerializer(serializers.Serializer):
    address = serializers.CharField()
    comment = serializers.CharField(required=False, allow_blank=True)

    items = serializers.ListField(
        child=serializers.DictField()
    )