import pytest
from rest_framework.test import APIClient

from api.v1.recipe.dto.recipe_dto import IngredientDTO, RecipeDTO, StepDTO
from api.v1.recipe.repositories.recipe_repository import RecipeRepository
from recipe.choices import MealType, Unit


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def repo():
    return RecipeRepository()

@pytest.fixture
def dto():
    return RecipeDTO(
            title="Омлет",
            description="Описание",
            meal_type=MealType.BREAKFAST.value,
            ingredients=[
                IngredientDTO(name="Egg", amount=2, unit=Unit.PC.value),
                IngredientDTO(name="Milk", amount=100, unit=Unit.ML.value)
            ],
            steps=[StepDTO(step="Step1")],
            tips="Совет",
            thumbnail=None
        )
