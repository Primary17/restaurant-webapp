from decimal import Decimal

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from orders.models import Order
from orders.services.cart_services import checkout_cart
from orders.services.order_service import create_order
from testing.factories import (
    create_addon_setup,
    create_dish,
    create_ingredient_option,
    create_user,
    ensure_cart,
)
from orders.models import CartItem


class OrderServiceTests(TestCase):
    def setUp(self):
        self.user = create_user()

    def test_create_order_calculates_total_with_addon(self):
        dish = create_dish(base_price=Decimal('100.00'))
        addon, _ = create_addon_setup(dish, price=Decimal('15.00'))
        option, _, _ = create_ingredient_option(dish)

        order = create_order(
            self.user,
            {
                'address': 'Kyiv, Test 1',
                'items': [
                    {
                        'dish_id': dish.pk,
                        'quantity': 2,
                        'addons': [addon.pk],
                        'ingredients': [option.pk],
                    }
                ],
            },
        )
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items_total, Decimal('230.00'))
        self.assertEqual(order.total_price, Decimal('230.00'))

    def test_create_order_rejects_empty_items(self):
        with self.assertRaises(ValidationError):
            create_order(self.user, {'address': 'Addr', 'items': []})

    def test_create_order_rejects_inactive_dish(self):
        dish = create_dish(is_active=False)
        with self.assertRaises(ValidationError):
            create_order(
                self.user,
                {
                    'address': 'Addr',
                    'items': [{'dish_id': dish.pk, 'quantity': 1}],
                },
            )

    def test_checkout_cart_clears_cart_and_creates_order(self):
        dish = create_dish(base_price=Decimal('50.00'))
        cart = ensure_cart(self.user)
        CartItem.objects.create(cart=cart, dish=dish, quantity=1)

        order = checkout_cart(
            self.user,
            {'address': 'Lviv, 10', 'phone': '+380000000000', 'comment': ''},
        )
        self.assertIsInstance(order, Order)
        self.assertEqual(cart.items.count(), 0)
        self.assertEqual(order.address, 'Lviv, 10')
        self.assertEqual(order.phone, '+380000000000')

    def test_checkout_empty_cart_raises(self):
        ensure_cart(self.user)
        with self.assertRaisesMessage(ValueError, 'порожній'):
            checkout_cart(self.user, {'address': 'Addr'})
