from django.core.exceptions import ValidationError

from api.v1.recipe.dto.recipe_dto import RecipeDTO
from api.v1.recipe.interfaces.recipe_parser import IRecipeRepository
from api.v1.recipe.services.image_service import ImageService
from app.models import StatusChoices
from recipe.models import Recipe, RecipeIngredient, RecipeSource
from product.models import Product


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
            raise ValidationError("Recipe already exists.") #TODO add other response for existing recipe
        
        return self._create_recipe_from_dto(dto, user_id, source_id)
    
    def create_from_dto(self, dto: RecipeDTO, user_id: str, source_id: str) -> Recipe:
        if self.exists_for_user(source_id, user_id):
            raise ValidationError("Recipe already exists.") #TODO add other response for existing recipe
        
        return self._create_recipe_from_dto(dto, user_id, source_id)

    def _create_recipe_from_dto(self, dto: RecipeDTO, user_id: str, source_id: str) -> Recipe:    
        recipe_source = RecipeSource.objects.get(id=source_id)

        recipe_obj = Recipe.objects.create(
            source=recipe_source,
            created_by_id=user_id,
            name=dto.title,
            description="\n".join(step.step for step in dto.steps), 
            meal_type=dto.meal_type or "",  #TODO maybe need to remove ""
            tips=dto.tips,
        )

        if dto.thumbnail:
            image_bytes, filename = ImageService.download_image(dto.thumbnail)
            ImageService.save_image_to_model(recipe_obj, "image", image_bytes, filename)
        
        for ing in dto.ingredients:
            product = Product.objects.filter(
                name__iexact=ing.name,
                created_by_id=user_id
            ).first()

            if not product:
                product = Product.objects.create(
                    name=ing.name,
                    created_by_id=user_id
                )
            
            RecipeIngredient.objects.create(
                recipe=recipe_obj,
                product=product,
                quantity=ing.amount,
                unit=ing.unit
            )

        return recipe_obj
    
    def update_source_parsed_data(self, source_id: str, parsed_data: dict):
        RecipeSource.objects.filter(id=source_id).update(
            parsed_recipe=parsed_data,
            status=StatusChoices.DONE
        )

    def get_parsed_data_from_source(self, source_id: str) -> dict:
        return RecipeSource.objects.get(id=source_id).parsed_recipe



