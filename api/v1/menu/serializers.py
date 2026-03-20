from rest_framework import serializers

from recipe.choices import MealType


class MenuEntryInputSerializer(serializers.Serializer):
    """Сериализатор для ручной записи в меню"""
    date = serializers.DateField()
    meal_type = serializers.ChoiceField(choices=MealType.choices)
    recipe_id = serializers.UUIDField()
    servings = serializers.IntegerField(min_value=1, max_value=50)


class CreateMenuSerializer(serializers.Serializer):
    """Сериализатор входных данных для создания меню"""
    name = serializers.CharField(max_length=255)
    servings = serializers.IntegerField(min_value=1, max_value=50, default=2)
    dates = serializers.ListField(
        child=serializers.DateField(),
        min_length=1,
        max_length=31,  # максимум месяц
    )
    meal_types = serializers.ListField(
        child=serializers.ChoiceField(choices=MealType.choices),
        min_length=1,
    )
    entries = MenuEntryInputSerializer(many=True, required=False, allow_null=True)



class UpdateMenuEntrySerializer(serializers.Serializer):
    """Сериализатор для обновления записи в меню"""
    recipe_id = serializers.UUIDField(required=False, allow_null=True)
    servings = serializers.IntegerField(min_value=1, max_value=50, required=False)
    date = serializers.DateField(required=False)
    meal_type = serializers.ChoiceField(choices=MealType.choices, required=False)

    
class SwapEntriesSerializer(serializers.Serializer):
    """Сериализатор для свопа двух записей в меню"""
    entry_id_1 = serializers.UUIDField()
    entry_id_2 = serializers.UUIDField()


class AddMenuEntrySerializer(serializers.Serializer):
    """Сериализатор для добавления новой записи в план"""
    plan_id = serializers.UUIDField()
    date = serializers.DateField()
    meal_type = serializers.ChoiceField(choices=MealType.choices)
    recipe_id = serializers.UUIDField()
    servings = serializers.IntegerField(min_value=1, max_value=50)


class ShoppingCartSerializer(serializers.Serializer):
    """Сериализатор для вывода корзины закупок"""
    product_name = serializers.CharField()
    product_id = serializers.CharField()
    category = serializers.CharField()
    quantity = serializers.FloatField()
    unit = serializers.CharField()
