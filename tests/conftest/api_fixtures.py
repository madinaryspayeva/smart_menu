import pytest
from rest_framework.test import APIClient

from api.v1.recipe.dto.recipe_dto import IngredientDTO, RecipeDTO, StepDTO
from api.v1.recipe.repositories.recipe_repository import RecipeRepository
from api.v1.recipe.services.recipe_builder import RecipeBuilderService
from api.v1.recipe.services.url_classifier import UrlClassifier
from api.v1.recipe.services.video_parser import VideoParserService
from api.v1.recipe.services.web_parser import WebParserService
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

@pytest.fixture
def classifier():
    return UrlClassifier()

@pytest.fixture
def video_parser():
    return VideoParserService()

@pytest.fixture
def web_parser():
    return WebParserService()

@pytest.fixture
def builder():
    return RecipeBuilderService()