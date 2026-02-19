from django.contrib import admin

from recipe.models import Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "servings", "meal_type", "image", ]
    search_fields = ("name",)