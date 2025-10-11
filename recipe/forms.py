# forms.py
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = False
            


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


class BaseRecipeIngredientFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        seen_products = {}
        duplicates = []

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            product = form.cleaned_data.get("product")
            if not product:
                continue
                
            product_id = product.id

            if product_id in seen_products:
                duplicates.append(product)
                form.add_error(
                    "product",
                    f"Продукт «{product.name}» уже добавлен в рецепте. Удалите дубликат."
                )
                seen_products[product_id].add_error(
                    "product",
                    f"Продукт «{product.name}» был добавлен ниже."
                )
            else:
                seen_products[product_id] = form
        
        if duplicates:
            duplicate_names = ", ".join(str(p) for p in duplicates)
            raise forms.ValidationError(
                f"Некоторые ингредиенты дублируются: {duplicate_names}."
            )

   

RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    fields=["product", "quantity", "unit"],
    extra=0,         
    can_delete=True,
    formset=BaseRecipeIngredientFormSet,
)
