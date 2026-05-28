from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from testing.factories import create_category, create_dish


class MenuAPITests(APITestCase):
    def test_categories_are_public(self):
        create_category(name='Pizza')
        response = self.client.get('/api/menu/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Pizza')

    def test_dishes_list_returns_only_active(self):
        create_dish(name='Active', is_active=True)
        create_dish(name='Hidden', is_active=False)
        response = self.client.get('/api/menu/dishes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [d['name'] for d in response.data]
        self.assertIn('Active', names)
        self.assertNotIn('Hidden', names)

    def test_dish_detail_not_found_for_inactive(self):
        dish = create_dish(is_active=False)
        response = self.client.get(f'/api/menu/dishes/{dish.pk}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_parent_category_includes_descendants(self):
        parent = create_category(name='Food')
        child = create_category(name='Burgers', parent=parent)
        in_tree = create_dish(name='Burger', category=child)
        other_cat = create_category(name='Drinks')
        create_dish(name='Cola', category=other_cat, base_price=Decimal('20.00'))

        response = self.client.get('/api/menu/dishes/', {'category': parent.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [d['name'] for d in response.data]
        self.assertEqual(names, ['Burger'])
        self.assertEqual(response.data[0]['id'], in_tree.pk)
