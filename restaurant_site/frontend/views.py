from django.shortcuts import render, get_object_or_404
from menu.models import Dish, Category
from django.template.loader import render_to_string
from django.http import JsonResponse

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
        ordering_fields = [f.strip() for f in ordering.split(',')]
        dishes = dishes.order_by(*ordering_fields)
    if price_max:
        dishes = dishes.filter(base_price__lte=price_max)

    # Фільтр по дієтах
    diet = request.GET.get('diet', '')
    if diet:
        diet_map = {
            'vegan': 'is_vegan',
            'vegetarian': 'is_vegetarian',
            'gluten_free': 'is_gluten_free',
            'lactose_free': 'is_lactose_free',
            'nut_free': 'is_nut_free',
        }
        for d in diet.split(','):
            if d in diet_map:
                dishes = dishes.filter(**{diet_map[d]: True})

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
        'diet': diet,
        'price_max': price_max or '1000',
    })

def menu_ajax(request):
    from django.db.models import Min, Max
    category_id = request.GET.get('category', '')
    search = request.GET.get('search', '')
    ordering = request.GET.get('ordering', '')

    price_range = Dish.objects.filter(is_active=True).aggregate(
        min=Min('base_price'), max=Max('base_price')
    )
    min_price = int(price_range['min'] or 0)
    max_price = int(price_range['max'] or 1000)

    price_min = int(request.GET.get('price_min', min_price))
    price_max = int(request.GET.get('price_max', max_price))

    dishes = Dish.objects.filter(is_active=True)

    # Фільтр по дієтах
    diet = request.GET.get('diet', '')
    if diet:
        diet_map = {
            'vegan': 'is_vegan',
            'vegetarian': 'is_vegetarian',
            'gluten_free': 'is_gluten_free',
            'lactose_free': 'is_lactose_free',
            'nut_free': 'is_nut_free',
        }
        for d in diet.split(','):
            if d in diet_map:
                dishes = dishes.filter(**{diet_map[d]: True})

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
        ordering_fields = [f.strip() for f in ordering.split(',')]
        dishes = dishes.order_by(*ordering_fields)

    dishes = dishes.filter(base_price__gte=price_min, base_price__lte=price_max)

    html = render_to_string('frontend/partials/dish_list.html', {'dishes': dishes}, request=request)
    return JsonResponse({'html': html})

def dish_detail(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    from menu.models import Ingredient, AddonCategory, Addon
    all_ingredients = Ingredient.objects.all()
    return render(request, 'frontend/dish.html', {
        'dish': dish,
        'all_ingredients': all_ingredients,
    })

def checkout(request):
    return render(request, 'frontend/checkout.html')


def staff_orders(request):
    return render(request, 'frontend/staff_orders.html')