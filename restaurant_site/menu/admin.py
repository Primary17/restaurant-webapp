import nested_admin
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from .models import *
from mptt.admin import MPTTModelAdmin



@admin.register(AddonCategory)
class AddonCategoryAdmin(MPTTModelAdmin):
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    search_fields = ['name']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Addon)
class AddonAdmin(admin.ModelAdmin):
    search_fields = ['name']


class IngredientOptionInline(nested_admin.NestedTabularInline):
    model = IngredientOption
    extra = 1
    autocomplete_fields = ['ingredient']


class IngredientGroupInline(nested_admin.NestedStackedInline):
    model = IngredientGroup
    extra = 1
    inlines = [IngredientOptionInline]


class DishAddonGroupInline(nested_admin.NestedStackedInline):
    model = DishAddonGroup
    extra = 1
    autocomplete_fields = ['category']

class DishImageInline(nested_admin.NestedTabularInline):
    model = DishImage
    extra = 1
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80"/>', obj.image.url)
        return "Немає фото"


@admin.register(Dish)
class DishAdmin(nested_admin.NestedModelAdmin):
    inlines = [
        DishImageInline,
        IngredientGroupInline,
        DishAddonGroupInline,
    ]

    list_display = ['name', 'category', 'base_price', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name']