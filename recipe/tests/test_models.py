from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from recipe.choices import MealType, Source, Unit
from recipe.models import RecipeIngredient, RecipeSource


@pytest.mark.django_db
class TestRecipeSourceModel:

    def test_str_method(self, recipe_source):
        expected = (
            f"Recipe Source: {recipe_source.url}, "
            f"{recipe_source.title}, {recipe_source.status}, "
            f"{recipe_source.source}, {recipe_source.parsed_recipe}, "
            f"{recipe_source.error_message}"
    )
        assert str(recipe_source) == expected
    
    def test_unique_url(self):
        RecipeSource.objects.create(url="https://unique.com", source=Source.WEBSITE)
        with pytest.raises(IntegrityError):
            RecipeSource.objects.create(url="https://unique.com", source=Source.WEBSITE)


@pytest.mark.django_db
class TestRecipeModel:

    def test_str_method(self, recipe):
        assert str(recipe) == recipe.name
    
    def test_meal_type_values(self, recipe):
        for mt in MealType:
            recipe.meal_type = mt.value
            recipe.full_clean(exclude=["source", "created_by"])
            assert recipe.meal_type == mt.value


@pytest.mark.django_db
class TestRecipeIngredientModel:

    def test_fields_and_str(self, ingredient):
        assert ingredient.recipe is not None
        assert ingredient.product is not None
        assert ingredient.quantity == Decimal("100")
        assert ingredient.unit == Unit.GR
        assert str(ingredient) == f"{ingredient.quantity} {ingredient.unit} {ingredient.product}"
    
    def test_quantity_positive_validation(self, recipe, product):
        invalid = RecipeIngredient(
            recipe=recipe, 
            product=product, 
            quantity=Decimal("-100"), 
            unit=Unit.GR
        )
        with pytest.raises(ValidationError):
            invalid.full_clean()
    
    def test_unit_values(self, ingredient):
        for u in Unit:
            ingredient.unit = u.value
            ingredient.full_clean()
            assert ingredient.unit == u.value
    
    def test_source_values(self, recipe_source):
        for s in Source:
            recipe_source.source = s.value
            recipe_source.full_clean()
            assert recipe_source.source == s.value