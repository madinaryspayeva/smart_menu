import pytest
from recipe.forms import (
    RecipeForm,
    RecipeIngredientForm,
    RecipeIngredientFormSet,
)
from recipe.choices import Unit


@pytest.mark.django_db
class TestRecipeForm:

    def test_meal_type_required(self):
        form = RecipeForm(
            data={
                "name": "Test Recipe",
                "servings": 2,
                "description": "Test description",
                "meal_type": "",
            }
        )

        assert not form.is_valid()
        assert "meal_type" in form.errors
    
    def test_image_not_required(self, valid_recipe_data):
        form = RecipeForm(data=valid_recipe_data)
        assert form.is_valid()


@pytest.mark.django_db
class TestRecipeIngredientForm:

    def test_unit_required(self, product_1):
        form = RecipeIngredientForm(
            data={
                "product": product_1.id,
                "quantity": 1,
                "unit": "",
            }
        )

        assert not form.is_valid()
        assert "unit" in form.errors
    
    def test_valid_ingredient_data(self, product_1):
        form = RecipeIngredientForm(
            data={
                "product": product_1.id,
                "quantity": 1.5,
                "unit": Unit.L
            }
        )

        assert form.is_valid()


@pytest.mark.django_db
class TestRecipeIngredientFormSet:

    def build_formset_data(self, products):
        prefix = "ingredient"

        data = {
        f"{prefix}-TOTAL_FORMS": str(len(products)),
        f"{prefix}-INITIAL_FORMS": "0",
        f"{prefix}-MIN_NUM_FORMS": "0",
        f"{prefix}-MAX_NUM_FORMS": "1000",
        }

        for i, product in enumerate(products):
            data[f"{prefix}-{i}-product"] = product.id
            data[f"{prefix}-{i}-quantity"] = "1"
            data[f"{prefix}-{i}-unit"] = "gr"

        return data

    def test_no_duplicates_valid(self, recipe, product_1, product_2):
        data = self.build_formset_data([product_1, product_2])
        formset = RecipeIngredientFormSet(data=data, instance=recipe)

        assert formset.is_valid()
        assert not formset.non_form_errors()
    
    def test_duplicate_products_invalid(self, recipe, product_1):
        data = self.build_formset_data([product_1, product_1])
        formset = RecipeIngredientFormSet(data=data, instance=recipe)

        assert not formset.is_valid()

        errors = formset.non_form_errors()
        assert len(errors) == 1
        assert "дублируются" in str(errors[0])

        assert "product" in formset.forms[0].errors
        assert "product" in formset.forms[1].errors
                                    