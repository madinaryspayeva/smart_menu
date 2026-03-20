from django.contrib import admin

from recipe.models import Recipe, RecipeSource


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "servings", "meal_type", "image", ]
    search_fields = ("name",)

@admin.register(RecipeSource)
class RecipeSourceAdmin(admin.ModelAdmin):
    list_display = ["url", "source", "title", "status", "parsed_recipe", "error_message", ]
    search_fields = ("title",)