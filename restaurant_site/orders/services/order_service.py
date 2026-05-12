from decimal import Decimal

from orders.models import Order, OrderItem, OrderItemAddon, OrderItemIngredient
from menu.models import Dish, Addon, IngredientOption


def create_order(user, data):
    items_data = data['items']

    order = Order.objects.create(
        user=user,
        items_total=Decimal('0.00'),
        total_price=Decimal('0.00'),
        address=data.get('address', ''),
        comment=data.get('comment', '')
    )

    total = Decimal('0.00')

    for item_data in items_data:
        dish = Dish.objects.get(id=item_data['dish_id'])

        item = OrderItem.objects.create(
            order=order,
            dish=dish,
            name=dish.name,
            base_price=dish.base_price,
            quantity=item_data.get('quantity', 1),
            total_price=Decimal('0.00')
        )

        item_total = dish.base_price

        # ADDONS
        for addon_id in item_data.get('addons', []):
            addon = Addon.objects.get(id=addon_id)

            OrderItemAddon.objects.create(
                item=item,
                addon=addon,
                name=addon.name,
                price=addon.price
            )

            item_total += addon.price

        # INGREDIENTS
        for ing_id in item_data.get('ingredients', []):
            ing = IngredientOption.objects.get(id=ing_id)

            OrderItemIngredient.objects.create(
                item=item,
                ingredient=ing.ingredient,
                name=ing.ingredient.name,
                price_delta=ing.price_delta
            )

            item_total += ing.price_delta

        item_total *= item.quantity

        item.total_price = item_total
        item.save()

        total += item_total

    order.items_total = total
    order.total_price = total + order.delivery_fee
    order.save()

    return order