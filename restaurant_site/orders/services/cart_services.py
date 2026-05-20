from orders.models import Cart
from orders.services.order_service import create_order


def checkout_cart(user, data):
    cart = Cart.objects.prefetch_related(
        'items__dish', 'items__addons', 'items__ingredients', 
        'items__removed_ingredients'
    ).select_related('user').get(user=user)

    if not cart.items.exists():
        raise ValueError('Кошик порожній.')

    items_data = []

    for item in cart.items.all():
        items_data.append({
            "dish_id": item.dish_id,
            "quantity": item.quantity,
            "addons": [a.addon_id for a in item.addons.all()], 
            "ingredients": [i.ingredient_option_id for i in item.ingredients.all()],
            "removed_ingredients": [r.ingredient_id for r in item.removed_ingredients.all()],
            "added_ingredients": [] 
        })

    order_data = {
        "items": items_data,
        "address": data.get("address"),
        "comment": data.get("comment", "")
    }

    order = create_order(user, order_data)

    cart.items.all().delete()

    return order