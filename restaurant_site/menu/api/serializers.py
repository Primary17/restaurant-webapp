from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from menu.models import (
    Addon,
    AddonCategory,
    Category,
    Dish,
    DishAddonGroup,
    DishImage,
    IngredientGroup,
    IngredientOption,
)


class AddonCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addon
        fields = ['id', 'name', 'price']


class IngredientOptionCatalogSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.IntegerField(source='ingredient.id', read_only=True)
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)

    class Meta:
        model = IngredientOption
        fields = [
            'id',
            'ingredient_id',
            'ingredient_name',
            'price_delta',
            'is_default',
        ]


class IngredientGroupCatalogSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = IngredientGroup
        fields = ['id', 'name', 'is_required', 'max_choices', 'options']

    @extend_schema_field(IngredientOptionCatalogSerializer(many=True))
    def get_options(self, obj):
        qs = obj.options.all().select_related('ingredient')
        return IngredientOptionCatalogSerializer(qs, many=True).data


class AddonCategoryBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddonCategory
        fields = ['id', 'name']


class DishAddonGroupCatalogSerializer(serializers.ModelSerializer):
    category = AddonCategoryBriefSerializer(read_only=True)
    addons = serializers.SerializerMethodField()

    class Meta:
        model = DishAddonGroup
        fields = ['id', 'category', 'is_required', 'max_choices', 'addons']

    @extend_schema_field(AddonCatalogSerializer(many=True))
    def get_addons(self, group):
        cat_ids = group.category.get_descendants(include_self=True).values_list(
            'pk', flat=True
        )
        addons = Addon.objects.filter(category_id__in=cat_ids)
        return AddonCatalogSerializer(addons, many=True).data


class DishImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = DishImage
        fields = ['id', 'url', 'is_main']

    def get_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        url = obj.image.url
        if request:
            return request.build_absolute_uri(url)
        return url


class DishListSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(source='category.id', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    main_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Dish
        fields = [
            'id',
            'name',
            'base_price',
            'category_id',
            'category_name',
            'is_active',
            'main_image_url',
        ]

    @extend_schema_field(
        serializers.URLField(allow_null=True, required=False, read_only=True)
    )
    def get_main_image_url(self, obj):
        img = obj.images.filter(is_main=True).first() or obj.images.first()
        if not img or not img.image:
            return None
        request = self.context.get('request')
        url = img.image.url
        if request:
            return request.build_absolute_uri(url)
        return url


class DishDetailSerializer(DishListSerializer):
    images = DishImageSerializer(many=True, read_only=True)
    addon_groups = DishAddonGroupCatalogSerializer(many=True, read_only=True)
    ingredient_groups = IngredientGroupCatalogSerializer(many=True, read_only=True)

    class Meta(DishListSerializer.Meta):
        fields = DishListSerializer.Meta.fields + [
            'images',
            'addon_groups',
            'ingredient_groups',
        ]


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'level', 'children']

    @extend_schema_field(serializers.ListSerializer(child=serializers.DictField()))
    def get_children(self, obj):
        children = obj.get_children()
        return CategoryTreeSerializer(
            children, many=True, context=self.context
        ).data
