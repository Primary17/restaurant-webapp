from decimal import Decimal

from menu.models import (
    Addon,
    AddonCategory,
    Category,
    Dish,
    DishAddonGroup,
    Ingredient,
    IngredientGroup,
    IngredientOption,
)
from orders.models import Cart
from users.models import User


def create_user(
    username='user1',
    password='testpass123',
    role=User.ROLE_CUSTOMER,
    **extra,
):
    user = User.objects.create_user(
        username=username,
        email=extra.pop('email', f'{username}@example.com'),
        password=password,
        role=role,
        **extra,
    )
    return user


def create_category(name='Main', parent=None):
    return Category.objects.create(name=name, parent=parent)


def create_dish(
    name='Test Dish',
    base_price=Decimal('100.00'),
    *,
    category=None,
    is_active=True,
):
    if category is None:
        category = create_category()
    return Dish.objects.create(
        name=name,
        category=category,
        base_price=base_price,
        is_active=is_active,
    )


def create_addon_setup(dish, *, addon_name='Extra', price=Decimal('10.00'), required=False):
    addon_cat = AddonCategory.objects.create(name=f'Addons for {dish.pk}')
    addon = Addon.objects.create(name=addon_name, category=addon_cat, price=price)
    DishAddonGroup.objects.create(
        dish=dish,
        category=addon_cat,
        is_required=required,
        max_choices=3,
    )
    return addon, addon_cat


def create_ingredient_option(dish, *, group_name='Size', price_delta=Decimal('0.00')):
    ingredient = Ingredient.objects.create(name=f'Ing-{dish.pk}')
    group = IngredientGroup.objects.create(
        dish=dish,
        name=group_name,
        is_required=True,
        max_choices=1,
    )
    option = IngredientOption.objects.create(
        group=group,
        ingredient=ingredient,
        price_delta=price_delta,
    )
    return option, ingredient, group


def ensure_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart
