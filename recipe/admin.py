from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from recipe.models import Recipe, RecipeIngredient




@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "servings", "meal_type", "image", ]
    search_fields = ("name",)