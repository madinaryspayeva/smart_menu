from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from recipe.models import RecipeSource
from app.models import StatusChoices
from api.v1.recipe.services.recipe_parser import RecipeParserService


@shared_task(bind=True, max_retries=3)
def parse_recipe_url(self, recipe_source_id):
    """
    Задача для парсинга URL рецепта
    """
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    try:
        recipe_source = RecipeSource.objects.get(id=recipe_source_id)
        recipe_source.status = StatusChoices.PROCESSING
        recipe_source.save()

        parser = RecipeParserService()
        parsed_data = parser.parse_recipe_from_url(recipe_source.url)
        recipe_source.parsed_recipe = parsed_data
        recipe_source.title = parsed_data.get("title", "Без названия")
        recipe_source.status = StatusChoices.DONE
        recipe_source.save()

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