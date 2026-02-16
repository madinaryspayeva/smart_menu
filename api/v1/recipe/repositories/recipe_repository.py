from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.db import transaction

from api.v1.recipe.dto.recipe_dto import RecipeDTO
from api.v1.recipe.interfaces.recipe_parser import IRecipeRepository
from api.v1.recipe.services.image_service import ImageService
from recipe.models import Recipe, RecipeIngredient, RecipeSource
from product.models import Product


class RecipeRepository(IRecipeRepository):
    def save(self, recipe_source_id: str, user_id: str, dto: RecipeDTO) -> Recipe:

        if Recipe.objects.filter(
            source_id=recipe_source_id,
            created_by_id=user_id
        ).exists():
            #TODO add userreadapble message that recipe already exists
            raise ValidationError(
                "Recipe already exists."
            )
            
        recipe_source = RecipeSource.objects.get(id=recipe_source_id)

        with transaction.atomic():
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