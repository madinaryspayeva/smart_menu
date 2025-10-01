# forms.py
from django import forms
from django.forms import inlineformset_factory
from recipe.choices import MealType, Unit
from recipe.models import Recipe, RecipeIngredient


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["name", "servings", "description", "image", "meal_type"]
        widgets = {
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "hidden",
                    "accept": "image/*",
                    "id": "id_image"
                }
            ),
        }

    meal_type = forms.ChoiceField(
        choices=[("", "Выберите тип блюда")] + list(MealType.choices),
        required=True,
        label="Тип блюда"
    )


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["product", "quantity", "unit"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-input"}),
            "quantity": forms.NumberInput(attrs={
                "class": "form-input",
                "min": "0",
                "step": "any",
                "inputmode": "decimal",  
                "pattern": "[0-9]*([.,][0-9]+)?"
            }),
            "unit": forms.Select(attrs={"class": "form-input"}),
        }
    
    unit = forms.ChoiceField(
        choices=[("", "Ед. изм.")] + list(Unit.choices),
        required=True,
        label="Единица измерения"
    )
   

RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    fields=["product", "quantity", "unit"],
    extra=0,         
    can_delete=True,
)
