import pytest
from decimal import Decimal
from recipe.choices import MealType, Source, Unit
from recipe.models import RecipeSource, Recipe, RecipeIngredient



@pytest.fixture
def recipe_source(db):
    return RecipeSource.objects.create(
        url="https://example.com/test",
        source=Source.WEBSITE,
        title="Test Source"
    )

@pytest.fixture
def recipe(db, user, recipe_source):
    return Recipe.objects.create(
        source=recipe_source,
        name="Test Recipe",
        description="Test description",
        meal_type=MealType.LUNCH,
        created_by=user
    )

@pytest.fixture
def ingredient(db, recipe, product):
    return RecipeIngredient.objects.create(
        recipe=recipe,
        product=product,
        quantity=Decimal("100"),
        unit=Unit.GR
    )

@pytest.fixture
def recipe(db):
    return Recipe.objects.create(
        name="Тестовый рецепт",
        servings=2,
        description="Описание",
        meal_type="breakfast",
    )

@pytest.fixture
def valid_recipe_data():
    return {
        "name": "Омлет",
        "servings": 2,
        "description": "Описание",
        "meal_type": MealType.choices[0][0],
    }

@pytest.fixture
def recipe_factory(db, owner, recipe_source):
    def create_recipe(name="Recipe", meal_type=MealType.LUNCH, products=None):
        recipe = Recipe.objects.create(
            source=recipe_source,
            name=name,
            description="Test description",
            meal_type=meal_type,
            created_by=owner
        )

        if products:
            for product in products:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    product=product,
                    quantity=Decimal("100"),
                    unit=Unit.GR
                )

        return recipe

    return create_recipe
