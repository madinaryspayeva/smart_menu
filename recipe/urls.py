from django.urls import path

from recipe.views import RecipeCreateView, RecipeListView

app_name = "recipe"

urlpatterns = [
    path("add/", RecipeCreateView.as_view(), name="add"),
    path("", RecipeListView.as_view(), name="list"),
]