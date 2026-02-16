from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from api.v1.recipe.repositories.recipe_repository import RecipeRepository
from api.v1.recipe.serializers import ParseUrlSerializer, RecipeSourceSerializer
from api.v1.recipe.services.url_classifier import UrlClassifier
from api.v1.recipe.tasks import parse_video_recipe, parse_web_recipe
from api.v1.recipe.usecases.create_recipe_usecase import CreateRecipeFromExistingSourceUseCase
from app.models import StatusChoices
from recipe.choices import Source
from recipe.models import RecipeSource


class ParseUrlAPIView(generics.CreateAPIView):
    serializer_class = ParseUrlSerializer
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        url = serializer.validated_data["url"]

        classifier = UrlClassifier()
        url_info = classifier.classify(url)

        recipe_source, created = RecipeSource.objects.get_or_create(
            url=url_info.final_url,
            defaults={
                "status": StatusChoices.PENDING,
                "source": url_info.source,
            }
        )

        repository = RecipeRepository()

        if not created:
            existing_recipe = repository.get_by_user_and_source(request.user.id, recipe_source.id)

            if existing_recipe:
                return Response(
                    {"message": "У вас уже есть этот рецепт",
                    "recipe_id": existing_recipe.id,},
                    status=status.HTTP_200_OK,
                )
            
            if recipe_source.status == StatusChoices.DONE:
                use_case = CreateRecipeFromExistingSourceUseCase(repository=repository) #TODO check ingredients and product saving
                recipe = use_case.execute(request.user.id, recipe_source.id)

                return Response(
                    {
                        "recipe_id": recipe.id,
                        "message": "Recipe created from existing source",
                    },
                    status=status.HTTP_201_CREATED,
                )
            
            if recipe_source.status == StatusChoices.PROCESSING: #TODO change logic
                return Response(
                    {
                        "id": recipe_source.id,
                        "status": recipe_source.get_status_display(),
                    },
                    status=status.HTTP_202_ACCEPTED,
                )

        if created or recipe_source.status in [ StatusChoices.ERROR, StatusChoices.PENDING ]: 
            recipe_source.status = StatusChoices.PROCESSING
            recipe_source.save(update_fields=["status"])
            
            if url_info.source == Source.WEBSITE:
                parse_web_recipe.delay(recipe_source.id, request.user.id, url_info.final_url)
            else:  
                parse_video_recipe.delay(recipe_source.id, request.user.id, url_info.final_url)
            
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
    