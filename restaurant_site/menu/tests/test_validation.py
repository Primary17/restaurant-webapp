from decimal import Decimal

from django.test import TestCase

from orders.services.validation_service import (
    validate_addons_for_dish,
    validate_order_line,
)
from testing.factories import create_addon_setup, create_dish, create_ingredient_option


class ValidationServiceTests(TestCase):
    def test_rejects_duplicate_addon_ids(self):
        dish = create_dish()
        addon, _ = create_addon_setup(dish)
        with self.assertRaisesMessage(ValueError, 'Дублікати'):
            validate_addons_for_dish(dish, [addon.pk, addon.pk])

    def test_rejects_unknown_addon(self):
        dish = create_dish()
        with self.assertRaisesMessage(ValueError, 'Невідомі додатки'):
            validate_addons_for_dish(dish, [99999])

    def test_required_addon_group_must_be_satisfied(self):
        dish = create_dish()
        create_addon_setup(dish, required=True)
        with self.assertRaisesMessage(ValueError, "Обов'язковий вибір"):
            validate_order_line(dish, [], [])

    def test_validate_order_line_accepts_valid_selection(self):
        dish = create_dish()
        addon, _ = create_addon_setup(dish, required=True)
        option, _, _ = create_ingredient_option(dish)
        validate_order_line(dish, [addon.pk], [option.pk])
