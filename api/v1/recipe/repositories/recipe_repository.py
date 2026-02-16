from django.core.exceptions import ValidationError
from django.db import transaction

from api.v1.recipe.dto.recipe_dto import IngredientDTO, RecipeDTO, StepDTO
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
    
    def create_from_dto(self, dto_dict: dict, user_id: str, source_id: str) -> Recipe:
        if self.exists_for_user(source_id, user_id):
            raise ValidationError("Recipe already exists.") #TODO add other response for existing recipe
        
        dto = self._restore_dto_from_dict(dto_dict)
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
    
    def _restore_dto_from_dict(self, dto_dict: dict) -> RecipeDTO:
        return RecipeDTO(
            title=dto_dict.get("title"),
            description=dto_dict.get("description"),
            meal_type=dto_dict.get("meal_type"),
            tips=dto_dict.get("tips"),
            thumbnail=dto_dict.get("thumbnail"),
            ingredients=[
                IngredientDTO(**ing)
                for ing in dto_dict.get("ingredients", [])
            ],
            steps=[
                StepDTO(**step)
                for step in dto_dict.get("steps", [])
            ],
        )

    
    def update_source_parsed_data(self, source_id: str, parsed_data: dict):
        source = RecipeSource.objects.get(id=source_id)
        source.parsed_recipe = parsed_data
        source.status = StatusChoices.DONE
        source.save(update_fields=["parsed_recipe", "status"])
    

    def get_parsed_data_from_source(self, source_id: str) -> dict:
        return RecipeSource.objects.get(id=source_id).parsed_recipe



