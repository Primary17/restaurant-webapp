from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from orders.models import CartItem, Order
from testing.factories import (
    create_addon_setup,
    create_dish,
    create_ingredient_option,
    create_user,
    ensure_cart,
)
from users.models import User


class OrdersAPITests(APITestCase):
    def setUp(self):
        self.customer = create_user(username='customer')
        self.staff = create_user(username='staff', role=User.ROLE_STAFF)
        self.other = create_user(username='other')

    def test_cart_requires_authentication(self):
        response = self.client.get('/api/orders/cart/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_to_cart_and_checkout(self):
        dish = create_dish(base_price=Decimal('80.00'))
        addon, _ = create_addon_setup(dish, price=Decimal('20.00'), required=True)
        option, _, _ = create_ingredient_option(dish)

        self.client.force_authenticate(user=self.customer)
        add_resp = self.client.post(
            '/api/orders/cart/items/',
            {
                'dish_id': dish.pk,
                'quantity': 1,
                'addons': [addon.pk],
                'ingredients': [option.pk],
            },
            format='json',
        )
        self.assertEqual(add_resp.status_code, status.HTTP_201_CREATED)

        checkout_resp = self.client.post(
            '/api/orders/cart/checkout/',
            {
                'address': 'Odesa, 5',
                'phone': '+380501112233',
                'comment': 'No onions',
            },
            format='json',
        )
        self.assertEqual(checkout_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(checkout_resp.data['address'], 'Odesa, 5')
        self.assertEqual(checkout_resp.data['phone'], '+380501112233')
        self.assertEqual(Order.objects.filter(user=self.customer).count(), 1)

        cart_resp = self.client.get('/api/orders/cart/')
        self.assertEqual(cart_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(cart_resp.data['items']), 0)

    def test_my_orders_lists_only_own_orders(self):
        dish = create_dish()
        Order.objects.create(
            user=self.customer,
            items_total=Decimal('10.00'),
            total_price=Decimal('10.00'),
            address='A',
        )
        Order.objects.create(
            user=self.other,
            items_total=Decimal('20.00'),
            total_price=Decimal('20.00'),
            address='B',
        )

        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/orders/my/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['address'], 'A')

    def test_staff_orders_forbidden_for_customer(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/orders/staff/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_list_all_orders(self):
        Order.objects.create(
            user=self.customer,
            items_total=Decimal('10.00'),
            total_price=Decimal('10.00'),
            address='X',
        )
        self.client.force_authenticate(user=self.staff)
        response = self.client.get('/api/orders/staff/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_order_detail_forbidden_for_other_customer(self):
        order = Order.objects.create(
            user=self.other,
            items_total=Decimal('10.00'),
            total_price=Decimal('10.00'),
            address='Secret',
        )
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f'/api/orders/{order.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_update_order_status(self):
        order = Order.objects.create(
            user=self.customer,
            items_total=Decimal('10.00'),
            total_price=Decimal('10.00'),
            address='Addr',
            status='pending',
        )
        self.client.force_authenticate(user=self.staff)
        response = self.client.patch(
            f'/api/orders/{order.pk}/status/',
            {'status': 'confirmed'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'confirmed')

    def test_customer_cannot_update_order_status(self):
        order = Order.objects.create(
            user=self.customer,
            items_total=Decimal('10.00'),
            total_price=Decimal('10.00'),
            address='Addr',
        )
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(
            f'/api/orders/{order.pk}/status/',
            {'status': 'confirmed'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_inactive_dish_to_cart_returns_400(self):
        dish = create_dish(is_active=False)
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            '/api/orders/cart/items/',
            {'dish_id': dish.pk, 'quantity': 1},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
