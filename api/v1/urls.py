from django.urls import path, include


urlpatterns = [
    path("recipe/", include("api.v1.recipe.urls")),
]