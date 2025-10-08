from django.urls import path

from recipe.views import (
    RecipeCreateView, 
    RecipeListView, 
    RecipeDetailView,
    RecipeDeleteView
)

app_name = "recipe"

urlpatterns = [
    path("add/", RecipeCreateView.as_view(), name="add"),
    path("", RecipeListView.as_view(), name="list"),
    path("<uuid:pk>/", RecipeDetailView.as_view(), name="detail"),
    path("<uuid:pk>/delete/", RecipeDeleteView.as_view(), name="delete"),
]