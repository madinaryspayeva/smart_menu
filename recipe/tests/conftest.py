import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from recipe.choices import MealType, Source, Unit
from recipe.models import RecipeSource, Recipe, RecipeIngredient
from product.models import Product

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@example.com", password="securepass")

@pytest.fixture
def product(db):
    return Product.objects.create(name="Apple")

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
def product_1(db):
    return Product.objects.create(name="Молоко")


@pytest.fixture
def product_2(db):
    return Product.objects.create(name="Сахар")


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
