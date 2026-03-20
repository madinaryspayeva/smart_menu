from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import ValidationError

from api.v1.recipe.constants import PRODUCT_SIMILARITY_THRESHOLD
from api.v1.recipe.dto.recipe_dto import RecipeDTO
from api.v1.recipe.interfaces.recipe_parser import IRecipeRepository
from api.v1.recipe.services.image_service import ImageService
from app.models import StatusChoices
from product.models import Product
from recipe.choices import MealType
from recipe.models import Recipe, RecipeIngredient, RecipeSource


class RecipeRepository(IRecipeRepository):

    def exists_for_user(self, source_id: str, user_id: str) -> bool:
        return Recipe.objects.filter(
            source_id=source_id,
            created_by_id=user_id
        ).exists()

    def get_by_user_and_source(self, source_id: str, user_id: str):
        return Recipe.objects.filter(
            source_id=source_id,
            created_by_id=user_id
        ).first()
    
    def save(self, source_id: str, user_id: str, dto: RecipeDTO) -> Recipe:
        if self.exists_for_user(source_id, user_id):
            raise ValidationError("Recipe already exists.") #TODO add other response for 
                                                                #existing recipe
        
        return self._create_recipe_from_dto(dto, user_id, source_id)
    
    def create_from_dto(self, dto: RecipeDTO, user_id: str, source_id: str) -> Recipe:
        if self.exists_for_user(source_id, user_id):
            raise ValidationError("Recipe already exists.") #TODO add other response for 
                                                                #existing recipe
        
        return self._create_recipe_from_dto(dto, user_id, source_id)

    def _create_recipe_from_dto(self, dto: RecipeDTO, user_id: str, source_id: str) -> Recipe:    
        recipe_source = RecipeSource.objects.get(id=source_id)

        recipe_obj = Recipe.objects.create(
            source=recipe_source,
            created_by_id=user_id,
            name=dto.title,
            description="\n".join(step.step for step in dto.steps), 
            meal_type=dto.meal_type or MealType.UNCATEGORIZED,
            tips=dto.tips,
        )

        if dto.thumbnail:
            image_bytes, filename = ImageService.download_image(dto.thumbnail)
            ImageService.save_image_to_model(recipe_obj, "image", image_bytes, filename)
        
        for ing in dto.ingredients:
            product = self._find_or_create_product(ing.name, user_id)
            
            RecipeIngredient.objects.create(
                recipe=recipe_obj,
                product=product,
                quantity=ing.amount,
                unit=ing.unit
            )

        return recipe_obj
    
    def _find_or_create_product(self, name: str, user_id: str) -> Product:
        """Ищет продукт по триграммному сходству; создаёт новый если не нашёл."""
        match = (
            Product.objects.filter(created_by_id=user_id)
            .annotate(similarity=TrigramSimilarity("name", name))
            .filter(similarity__gte=PRODUCT_SIMILARITY_THRESHOLD)
            .order_by("-similarity")
            .first()
        )
        if match:
            return match
        return Product.objects.create(name=name, created_by_id=user_id)

    def update_source_parsed_data(self, source_id: str, parsed_data: dict):
        RecipeSource.objects.filter(id=source_id).update(
            parsed_recipe=parsed_data,
            status=StatusChoices.DONE
        )

    def get_parsed_data_from_source(self, source_id: str) -> dict:
        return RecipeSource.objects.get(id=source_id).parsed_recipe
