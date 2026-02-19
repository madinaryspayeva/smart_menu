from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from app.models import StatusChoices
from recipe.choices import MealType
from recipe.models import Recipe, RecipeIngredient


@pytest.mark.django_db
class TestRecipeRepository:

    def test_exists_for_user_true_and_false(self, repo, owner, recipe_source_api):
        assert not repo.exists_for_user(recipe_source_api.id, owner.id)

        Recipe.objects.create(
            source=recipe_source_api,
            created_by=owner,
            name="Омлет",
            description="Desc",
            meal_type=MealType.BREAKFAST
        )

        assert repo.exists_for_user(recipe_source_api.id, owner.id)
    
    def test_create_from_dto_creates_recipe_and_ingredients(
            self, repo, owner, recipe_source_api, dto
            ):
        with patch(
            "api.v1.recipe.services.image_service.ImageService.download_image"
        ) as mock_download, patch(
            "api.v1.recipe.services.image_service.ImageService.save_image_to_model"
        ):
            mock_download.return_value = (b"bytes", "file.jpg")

            recipe = repo.create_from_dto(dto, user_id=owner.id, source_id=recipe_source_api.id)
        
        assert recipe.id is not None
        assert recipe.name == dto.title
        assert RecipeIngredient.objects.filter(recipe=recipe).count() == len(dto.ingredients)
        for ing in dto.ingredients:
            assert RecipeIngredient.objects.filter(recipe=recipe, product__name=ing.name).exists()
    
    def test_save_raises_if_exists(self, repo, owner, recipe_source, dto):
        Recipe.objects.create(
            source=recipe_source,
            created_by=owner,
            name=dto.title,
            description=dto.description,
            meal_type=dto.meal_type
        )

        with pytest.raises(ValidationError):
            repo.save(source_id=recipe_source.id, user_id=owner.id, dto=dto)
    
    def test_create_from_dto_raises_if_exists(self, repo, owner, recipe_source_api, dto):
        Recipe.objects.create(
            source=recipe_source_api,
            created_by=owner,
            name=dto.title,
            description=dto.description,
            meal_type=dto.meal_type
        )

        with pytest.raises(ValidationError):
            repo.create_from_dto(dto, user_id=owner.id, source_id=recipe_source_api.id)
    
    def test_get_by_user_and_source(self, repo, owner, recipe_source_api):
        assert repo.get_by_user_and_source(recipe_source_api.id, owner.id) is None

        recipe = Recipe.objects.create(
            source=recipe_source_api,
            created_by=owner,
            name="Омлет",
            description="Desc",
            meal_type=MealType.BREAKFAST
            )
        
        fetched = repo.get_by_user_and_source(recipe_source_api.id, owner.id)

        assert fetched.id == recipe.id
    
    def test_update_and_get_parsed_data(self, repo, recipe_source):
        data = {"steps": ["Mix ingredients"]}
        repo.update_source_parsed_data(recipe_source.id, data)
        parsed = repo.get_parsed_data_from_source(recipe_source.id)
        assert parsed == data
        recipe_source.refresh_from_db()
        assert recipe_source.status == StatusChoices.DONE