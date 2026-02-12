from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from api.v1.recipe.services.image_service import ImageService
from api.v1.recipe.services.recipe_builder import RecipeBuilderService
from product.models import Product
from recipe.models import Recipe, RecipeIngredient, RecipeSource
from app.models import StatusChoices
from api.v1.recipe.services.recipe_parser import WebParserService
from api.v1.recipe.services.video_parser import VideoParserService
from api.v1.recipe.services.llm import LLMService


@shared_task(bind=True, max_retries=3)
def parse_recipe_url(self, recipe_source_id, request_user_id):
    """
    Задача для парсинга URL рецепта
    """
 
    try:
        recipe_source = RecipeSource.objects.get(id=recipe_source_id)
        recipe_source.status = StatusChoices.PROCESSING
        recipe_source.save()

        parser = WebParserService()
        raw_data = parser.parse_recipe_from_url(recipe_source.url)

        parsed_data = RecipeBuilderService().build_recipe(raw_data)
        recipe_source.parsed_recipe = parsed_data
        recipe_source.title = parsed_data.get("title", "Без названия")
        recipe_source.status = StatusChoices.DONE
        recipe_source.save()

        if recipe_source.status == StatusChoices.DONE and recipe_source.parsed_recipe:
                parsed = recipe_source.parsed_recipe
                with transaction.atomic():
                    recipe = Recipe.objects.create(
                        source=recipe_source,
                        created_by_id=request_user_id,
                        name=parsed.get("title"),
                        description="\n".join(step.get("step", "") for step in parsed.get("steps", [])),
                        meal_type=parsed.get("meal_type") or "",
                        tips=parsed.get("tips"),
                    )

                    thumbnail_url = parsed.get("thumbnail")
                    if thumbnail_url:
                        image_bytes, filename = ImageService.download_image(thumbnail_url)
                        ImageService.save_image_to_model(recipe, "image", image_bytes, filename)

                    for ing in parsed.get("ingredients", []):
                        quantity = ing.get("amount")
                        unit = ing.get("unit")

                        product = Product.objects.filter(
                            name__iexact=ing.get("name"),
                            created_by_id=request_user_id,
                        ).first()

                        if not product:
                            product = Product.objects.create(
                                name=ing.get("name"),
                                created_by_id=request_user_id,
                            )
                        
                        RecipeIngredient.objects.create(
                            recipe=recipe,
                            product=product,
                            quantity=quantity,
                            unit=unit
                        )
      
        return {
            'status': 'success', 
            'recipe_source_id': recipe_source_id,
            'title': parsed_data.get('title')
        }
    
    except ObjectDoesNotExist:
        self.retry(countdown=60)
    except Exception as e:
        recipe_source.status = StatusChoices.ERROR
        recipe_source.error_message = str(e)
        recipe_source.save()
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, max_retries=3)
def parse_video_url(self, recipe_source_id, request_user_id):
    """
    Задача для парсинга video рецепта
    """
 
    try:
        recipe_source = RecipeSource.objects.get(id=recipe_source_id)
        recipe_source.status = StatusChoices.PROCESSING
        recipe_source.save()

        parser = VideoParserService()
        video_data = parser.parse_video(recipe_source.url)
    
        llm_parser = LLMService()
        normalized_data = llm_parser.extract_recipe(video_data["description"] + " " + video_data["transcript"])  

        parsed_data = RecipeBuilderService().build_recipe(normalized_data)
        parsed_data["thumbnail"] = video_data["thumbnail"]

        recipe_source.parsed_recipe = parsed_data
        recipe_source.title = parsed_data.get("title", "Без названия")
        recipe_source.status = StatusChoices.DONE
        recipe_source.save()

        if recipe_source.status == StatusChoices.DONE and recipe_source.parsed_recipe:
                parsed = recipe_source.parsed_recipe
                with transaction.atomic():
                    recipe = Recipe.objects.create(
                        source=recipe_source,
                        created_by_id=request_user_id,
                        name=parsed.get("title"),
                        description="\n".join(step.get("step", "") for step in parsed.get("steps", [])),
                        meal_type=parsed.get("meal_type") or "",
                        tips=parsed.get("tips"),
                    )

                    thumbnail_url = parsed.get("thumbnail")
                    if thumbnail_url:
                        image_bytes, filename = ImageService.download_image(thumbnail_url)
                        ImageService.save_image_to_model(recipe, "image", image_bytes, filename)

                    for ing in parsed.get("ingredients", []):
                        quantity = ing.get("amount")
                        unit = ing.get("unit")

                        product = Product.objects.filter(
                            name__iexact=ing.get("name"),
                            created_by_id=request_user_id,
                        ).first()

                        if not product:
                            product = Product.objects.create(
                                name=ing.get("name"),
                                created_by_id=request_user_id,
                            )
                        
                        RecipeIngredient.objects.create(
                            recipe=recipe,
                            product=product,
                            quantity=quantity,
                            unit=unit
                        )

        return {
            'status': 'success', 
            'recipe_source_id': recipe_source_id,
            'title': parsed_data.get('title')
        }
    
    except ObjectDoesNotExist:
        self.retry(countdown=60)
    except Exception as e:
        recipe_source.status = StatusChoices.ERROR
        recipe_source.error_message = str(e)
        recipe_source.save()
        return {'status': 'error', 'error': str(e)}
    