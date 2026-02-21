from django.urls import include, path

urlpatterns = [
    path("recipe/", include("api.v1.recipe.urls")),
]