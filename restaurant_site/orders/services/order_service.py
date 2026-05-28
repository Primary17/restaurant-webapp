from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError

from menu.models import Addon, Dish, IngredientOption, Ingredient
from orders.models import (
    Order, 
    OrderItem, 
    OrderItemAddon, 
    OrderItemIngredient, 
    OrderItemRemovedIngredient
)
from orders.services.validation_service import validate_order_line

@transaction.atomic
def create_order(user, data, validate_line=True):
    items_data = data["items"]
    if not items_data:
        raise ValidationError({"items": "Потрібен хоча б один товар у замовленні."})

    order = Order.objects.create(
        user=user,
        items_total=Decimal("0.00"),
        total_price=Decimal("0.00"),
        address=data.get("address", ""),
        phone=data.get("phone", ""),
        comment=data.get("comment", ""),
    )

    total = Decimal("0.00")

    for item_data in items_data:
        try:
            dish = Dish.objects.get(pk=item_data["dish_id"])
        except Dish.DoesNotExist as exc:
            raise ValidationError(
                {"items": "Страву з id=%s не знайдено." % item_data.get("dish_id")}
            ) from exc

        if not dish.is_active:
            raise ValidationError(
                {"items": "Страва «%s» наразі недоступна." % dish.name}
            )

        addon_ids = item_data.get("addons") or []
        ing_ids = item_data.get("ingredients") or []
        removed_ing_ids = item_data.get("removed_ingredients") or []
        added_ing_ids = item_data.get("added_ingredients") or []

        if validate_line:
            try:
                validate_order_line(dish, addon_ids, ing_ids, removed_ing_ids, added_ing_ids)
            except ValueError as exc:
                raise ValidationError({"items": str(exc)}) from exc

        item = OrderItem.objects.create(
            order=order,
            dish=dish,
            name=dish.name,
            base_price=dish.base_price,
            quantity=item_data.get("quantity", 1),
            total_price=Decimal("0.00"),
        )

        item_total = dish.base_price

        for addon_id in addon_ids:
            addon = Addon.objects.get(pk=addon_id)
            OrderItemAddon.objects.create(
                item=item,
                addon=addon,
                name=addon.name,
                price=addon.price,
            )
            item_total += addon.price

        for ing_id in ing_ids:
            ing = IngredientOption.objects.get(pk=ing_id)
            group_name_lower = ing.group.name.lower()
            
            if "розмір" in group_name_lower or "об'єм" in group_name_lower or "обєм" in group_name_lower:

                calculated_delta = (dish.base_price * ing.price_delta / Decimal("100.00")).quantize(Decimal("0.01"))
            else:

                calculated_delta = ing.price_delta

            OrderItemIngredient.objects.create(
                item=item,
                ingredient=ing.ingredient,
                name=ing.ingredient.name,
                price_delta=calculated_delta,
            )
            item_total += calculated_delta

        for ing_id in removed_ing_ids:
            ing = Ingredient.objects.get(pk=ing_id)
            OrderItemRemovedIngredient.objects.create(
                item=item,
                ingredient=ing,
                name=ing.name
            )

        item_total *= item.quantity

        item.total_price = item_total
        item.save()

        total += item_total

    order.items_total = total
    order.total_price = total + order.delivery_fee
    order.save()

    return order
