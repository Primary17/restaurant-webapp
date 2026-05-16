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

    dishes = Dish.objects.filter(is_active=True)

    if category_id:
        dishes = dishes.filter(category_id=category_id)
    if search:
        dishes = dishes.filter(name__icontains=search)
    if ordering:
        dishes = dishes.order_by(ordering)

    categories = Category.objects.filter(level=0)

    return render(request, 'frontend/menu.html', {
        'dishes': dishes,
        'categories': categories,
        'selected_category': category_id,
        'search': search,
        'ordering': ordering,
    })

def dish_detail(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    return render(request, 'frontend/dish.html', {'dish': dish})