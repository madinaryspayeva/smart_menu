from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from api.v1.recipe.serializers import ParseUrlSerializer, RecipeSourceSerializer
from api.v1.recipe.services.url_classifier import UrlClassifier
from api.v1.recipe.tasks import parse_recipe_url, parse_video_url
from app.models import StatusChoices
from product.models import Product
from recipe.choices import MealType, Source
from recipe.models import Recipe, RecipeIngredient, RecipeSource


class ParseUrlAPIView(generics.CreateAPIView):
    serializer_class = ParseUrlSerializer
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = serializer.validated_data["url"]

        classifier = UrlClassifier()
        url_info = classifier.classify(url)

        recipe_source, created = RecipeSource.objects.get_or_create(
            url=url,
            defaults={
                "status": StatusChoices.PENDING,
                "source": url_info.source,
            }
        )

        if created or recipe_source.status in [ StatusChoices.ERROR, ]:
            recipe_source.status = StatusChoices.PROCESSING
            recipe_source.save(update_fields=["status"])
            
            if url_info.source == Source.WEBSITE:
                parse_recipe_url.delay(recipe_source.id, request.user.id)
            else:  
                parse_video_url.delay(recipe_source.id, request.user.id)
        
        recipe = None
        if recipe_source.status == StatusChoices.DONE and recipe_source.parsed_recipe:
            parsed = recipe_source.parsed_recipe
            with transaction.atomic():
                recipe = Recipe.objects.create(
                    source=recipe_source,
                    created_by=request.user,
                    name=parsed.get("title"),
                    description="\n".join(step.get("step", "") for step in parsed.get("steps", [])),
                    meal_type=parsed.get("meal_type") or "",
                    tips=parsed.get("tips"),
                    image=parsed.get("thumbnail"),
                )

                for ing in parsed.get("ingredients", []):
                    quantity = ing.get("amount")
                    unit = ing.get("unit")

                    product = Product.objects.filter(
                        name__iexact=ing.get("name"),
                        created_by=request.user,
                    ).first()

                    if not product:
                        product = Product.objects.create(
                            name=ing.get("name"),
                            created_by=request.user,
                        )
                    
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        product=product,
                        quantity=quantity,
                        unit=unit
                    )

            
        return Response({
            "id": recipe_source.id,
            "status": recipe_source.get_status_display(),
            "url": recipe_source.url,
            "created": created,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    

class ParseUrlSatusAPIView(generics.RetrieveAPIView):
    serializer_class = RecipeSourceSerializer 


    def get_object(self):
        return get_object_or_404(RecipeSource, id=self.kwargs["id"])