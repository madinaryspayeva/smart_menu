from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from api.v1.recipe.serializers import ParseUrlSerializer, RecipeSourceSerializer
from app.models import StatusChoices
from recipe.models import RecipeSource


class ParseUrlAPIView(generics.CreateAPIView):
    serializer_class = ParseUrlSerializer
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        url = serializer.validated_data["url"]

        recipe_source, created = RecipeSource.objects.get_or_create(
            url=url,
            defaults={
                "status": StatusChoices.PENDING,
            }
        )

        if created or recipe_source.status in [
            StatusChoices.PENDING,
            StatusChoices.ERROR,
        ]:
            print("PEEEEENDIIIIING") #ADD CELERY TASK
        
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