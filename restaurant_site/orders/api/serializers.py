from decimal import Decimal
from rest_framework import serializers

from menu.models import Addon, Ingredient
from orders.models import (
    Cart,
    CartItem,
    CartItemAddon,
    CartItemIngredient,
    CartItemRemovedIngredient,
    CartItemAddedIngredient,
    Order,
    OrderItem,
    OrderItemAddon,
    OrderItemIngredient,
    OrderItemRemovedIngredient,
    OrderItemAddedIngredient,
)

class OrderItemAddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemAddon
        fields = ['id', 'name', 'price']


class OrderItemIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemIngredient
        fields = ['id', 'name', 'price_delta']


class OrderItemRemovedIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemRemovedIngredient
        fields = ['id', 'name']


class OrderItemAddedIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemAddedIngredient
        fields = ['id', 'name', 'price']

class OrderItemSerializer(serializers.ModelSerializer):
    addons = OrderItemAddonSerializer(many=True)
    ingredients = OrderItemIngredientSerializer(many=True)
    removed_ingredients = OrderItemRemovedIngredientSerializer(many=True, read_only=True)
    added_ingredients = OrderItemAddedIngredientSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'name', 'base_price', 'quantity', 'total_price',
            'addons', 'ingredients', 'removed_ingredients', 'added_ingredients'
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'items_total', 'delivery_fee', 'total_price',
            'address', 'comment', 'items', 'created_at'
        ]


class CreateOrderSerializer(serializers.Serializer):
    address = serializers.CharField()
    comment = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(child=serializers.DictField())


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
    ingredient_option_id = serializers.IntegerField(source='ingredient_option.id', read_only=True)
    ingredient_name = serializers.CharField(source='ingredient_option.ingredient.name', read_only=True)
    price_delta = serializers.SerializerMethodField()

    class Meta:
        model = CartItemIngredient
        fields = ['id', 'ingredient_option_id', 'ingredient_name', 'price_delta']

    def get_price_delta(self, obj):
        option = obj.ingredient_option
        dish = obj.item.dish  
        group_name_lower = option.group.name.lower()

        if "розмір" in group_name_lower or "об'єм" in group_name_lower or "обєм" in group_name_lower:
            delta = (dish.base_price * option.price_delta / Decimal("100.00")).quantize(Decimal("0.01"))
            return str(delta)
        
        return str(option.price_delta)

class CartItemRemovedIngredientSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)

    class Meta:
        model = CartItemRemovedIngredient
        fields = ['id', 'ingredient_id', 'name']

#СЕРІАЛІЗАТОР для читання доданих інгредієнтів/соусів у кошику
class CartItemAddedIngredientReadSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    price = serializers.CharField(source='ingredient.price', read_only=True)

    class Meta:
        model = CartItemAddedIngredient
        fields = ['id', 'ingredient_id', 'name', 'price']

class CartItemReadSerializer(serializers.ModelSerializer):
    dish_id = serializers.IntegerField(source='dish.id', read_only=True)
    dish_name = serializers.CharField(source='dish.name', read_only=True)
    addons = CartItemAddonReadSerializer(many=True, read_only=True)
    ingredients = CartItemIngredientReadSerializer(many=True, read_only=True)
    removed_ingredients = CartItemRemovedIngredientSerializer(many=True, read_only=True)
    added_ingredients = CartItemAddedIngredientReadSerializer(many=True, read_only=True)
    
    price_per_unit = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'dish_id', 'dish_name', 'quantity', 'price_per_unit', 
            'total_price', 'addons', 'ingredients', 'removed_ingredients', 'added_ingredients'
        ]

    def get_price_per_unit(self, obj):
        dish = obj.dish
        item_total = dish.base_price

        for cart_addon in obj.addons.all():
            item_total += cart_addon.addon.price

        for cart_ing in obj.ingredients.all():
            option = cart_ing.ingredient_option
            group_name_lower = option.group.name.lower()

            if "розмір" in group_name_lower or "об'єм" in group_name_lower or "обєм" in group_name_lower:
                delta = (dish.base_price * option.price_delta / Decimal("100.00")).quantize(Decimal("0.01"))
            else:
                delta = option.price_delta
            item_total += delta


        for added_ing in obj.added_ingredients.all():
            item_total += added_ing.ingredient.price

        return float(item_total)

    def get_total_price(self, obj):
        price_unit = self.get_price_per_unit(obj)
        return float(Decimal(str(price_unit)) * obj.quantity)


class AddCartItemSerializer(serializers.Serializer):
    dish_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, default=1)
    addons = serializers.ListField(child=serializers.IntegerField(min_value=1), required=False, default=list)
    ingredients = serializers.ListField(child=serializers.IntegerField(min_value=1), required=False, default=list)
    removed_ingredients = serializers.ListField(child=serializers.IntegerField(min_value=1), required=False, default=list)
    added_ingredients = serializers.ListField(child=serializers.IntegerField(min_value=1), required=False, default=list)

class CartItemQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemReadSerializer(many=True, read_only=True)
    cart_total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['cart_total_price', 'items']

    def get_cart_total_price(self, obj):
        total = Decimal("0.00")
        
        serialized_items = self.fields['items'].to_representation(obj.items.all())
        
        for item_data in serialized_items:
            total += Decimal(str(item_data['total_price']))
            
        return float(total)
