from django import forms
from django.forms import inlineformset_factory
from recipe.models import Recipe, RecipeIngredient


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["name", "servings", "description", "image", "meal_type"]


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["product", "quantity", "unit"]

RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    fields=["product", "quantity", "unit"],
    extra=1,
    can_delete=True,
)