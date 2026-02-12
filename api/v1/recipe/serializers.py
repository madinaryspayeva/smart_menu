from rest_framework import serializers
from recipe.models import RecipeSource


class ParseUrlSerializer(serializers.Serializer):
    url = serializers.URLField()


class RecipeSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeSource
        fields = [
            "id",
            "url",
            "source",
            "title",
            "status",
            "metadata",
            "parsed_recipe",
        ]
        read_only_fields = fields
