from rest_framework import serializers

from menu.models import Addon
from orders.models import (
    CartItem,
    CartItemAddon,
    CartItemIngredient,
    Order,
    OrderItem,
    OrderItemAddon,
    OrderItemIngredient,
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


class CheckoutSerializer(serializers.Serializer):
    address = serializers.CharField()
    comment = serializers.CharField(required=False, allow_blank=True)


class AddonRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addon
        fields = ['id', 'name', 'price']


class CartItemAddonReadSerializer(serializers.ModelSerializer):
    addon = AddonRefSerializer(read_only=True)

    class Meta:
        model = CartItemAddon
        fields = ['id', 'addon']


class CartItemIngredientReadSerializer(serializers.ModelSerializer):
    ingredient_option_id = serializers.IntegerField(
        source='ingredient_option.id', read_only=True
    )
    ingredient_name = serializers.CharField(
        source='ingredient_option.ingredient.name', read_only=True
    )
    price_delta = serializers.DecimalField(
        source='ingredient_option.price_delta',
        max_digits=6,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItemIngredient
        fields = ['id', 'ingredient_option_id', 'ingredient_name', 'price_delta']


class CartItemReadSerializer(serializers.ModelSerializer):
    dish_id = serializers.IntegerField(source='dish.id', read_only=True)
    dish_name = serializers.CharField(source='dish.name', read_only=True)
    addons = CartItemAddonReadSerializer(many=True, read_only=True)
    ingredients = CartItemIngredientReadSerializer(many=True, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'dish_id', 'dish_name', 'quantity', 'addons', 'ingredients']


class AddCartItemSerializer(serializers.Serializer):
    dish_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, default=1)
    addons = serializers.ListField(
        child=serializers.IntegerField(min_value=1), required=False, default=list
    )
    ingredients = serializers.ListField(
        child=serializers.IntegerField(min_value=1), required=False, default=list
    )


class CartItemQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)