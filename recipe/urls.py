from django.urls import path

from recipe.views import (
    MyRecipeListView,
    RecipeCreateView,
    RecipeDeleteView,
    RecipeDetailView,
    RecipeListView,
    RecipeUpdateView,
)

app_name = "recipe"

urlpatterns = [
    path("add/", RecipeCreateView.as_view(), name="add"),
    path("my/", MyRecipeListView.as_view(), name="my_list"),
    path("", RecipeListView.as_view(), name="list"),
    path("<uuid:pk>/", RecipeDetailView.as_view(), name="detail"),
    path("<uuid:pk>/delete/", RecipeDeleteView.as_view(), name="delete"),
    path("<uuid:pk>/edit/", RecipeUpdateView.as_view(), name="edit"),
]