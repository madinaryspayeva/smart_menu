from django.urls import path
from . import views


app_name = 'recipe_api_v1'


urlpatterns = [
    path("parse-url/", views.ParseUrlAPIView.as_view(), name="parse-url"),
    path("parse-url/<uuid:id>/", views.ParseUrlSatusAPIView.as_view(), name="parse-url-status"),
]