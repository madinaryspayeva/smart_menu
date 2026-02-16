from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from api.v1.recipe.repositories.recipe_repository import RecipeRepository
from api.v1.recipe.services.image_service import ImageService
from api.v1.recipe.services.recipe_builder import RecipeBuilderService
from api.v1.recipe.usecases.create_recipe_usecase import CreateRecipeUseCase
from product.models import Product
from recipe.models import Recipe, RecipeIngredient, RecipeSource
from app.models import StatusChoices
from api.v1.recipe.services.web_parser import WebParserService
from api.v1.recipe.services.video_parser import VideoParserService
from api.v1.recipe.services.llm import LLMService


@shared_task(bind=True, max_retries=3)
def parse_web_recipe(self, source_id: str, user_id: str, url: str):
    """
    Задача для парсинга web рецепта
    """

    use_case = CreateRecipeUseCase(
        parser=WebParserService(),
        builder=RecipeBuilderService(),
        repository=RecipeRepository(),
    )

    use_case.execute(source_id, user_id, url)
 
    


@shared_task(bind=True, max_retries=3)
def parse_video_recipe(self, source_id: str, user_id: str, url: str):
    """
    Задача для парсинга video рецепта
    """
 
    use_case = CreateRecipeUseCase(
        parser=VideoParserService(),
        builder=RecipeBuilderService(),
        repository=RecipeRepository(),
    )

    use_case.execute(source_id, user_id, url)
    