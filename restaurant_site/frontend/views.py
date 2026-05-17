from django.shortcuts import render, get_object_or_404
from menu.models import Dish, Category


def index(request):
    dishes = Dish.objects.filter(is_active=True)[:6]
    categories = Category.objects.filter(level=0)
    return render(request, 'frontend/index.html', {
        'dishes': dishes,
        'categories': categories,
    })


def menu(request):
    category_id = request.GET.get('category', '')
    search = request.GET.get('search', '')
    ordering = request.GET.get('ordering', '')
    price_max = request.GET.get('price_max', '')

    dishes = Dish.objects.filter(is_active=True)

    if category_id:
        try:
            cat = Category.objects.get(id=category_id)
            descendants = cat.get_descendants(include_self=True)
            dishes = dishes.filter(category__in=descendants)
        except Category.DoesNotExist:
            pass

    if search:
        dishes = dishes.filter(name__icontains=search)
    if ordering:
        dishes = dishes.order_by(ordering)
    if price_max:
        dishes = dishes.filter(base_price__lte=price_max)

    cats_with_dishes = set(
        Dish.objects.filter(is_active=True).values_list('category_id', flat=True)
    )
    categories = []
    for cat in Category.objects.filter(level=0):
        descendants = cat.get_descendants(include_self=True)
        if descendants.filter(id__in=cats_with_dishes).exists():
            categories.append(cat)

    root_category_id = ''
    if category_id:
        try:
            cat = Category.objects.get(id=category_id)
            root = cat.get_root()
            root_category_id = str(root.id)
        except Category.DoesNotExist:
            pass

    return render(request, 'frontend/menu.html', {
        'dishes': dishes,
        'categories': categories,
        'selected_category': category_id,
        'root_category_id': root_category_id,
        'search': search,
        'ordering': ordering,
        'price_max': price_max or '1000',
    })


def dish_detail(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    return render(request, 'frontend/dish.html', {'dish': dish})