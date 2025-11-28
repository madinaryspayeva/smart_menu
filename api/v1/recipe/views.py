from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from api.v1.recipe.serializers import ParseUrlSerializer, RecipeSourceSerializer
from recipe.models import RecipeSource