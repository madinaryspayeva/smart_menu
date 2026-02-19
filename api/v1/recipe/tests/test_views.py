from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse

from app.models import StatusChoices
from recipe.choices import Source
from recipe.models import Recipe, RecipeSource


@pytest.mark.django_db
class TestParseUrlAPIView:
    @patch("api.v1.recipe.views.parse_web_recipe.delay")
    @patch("api.v1.recipe.views.UrlClassifier.classify")
    def test_create_new_source_triggers_task(
        self,
        mock_classify,
        mock_task,
        auth_client,
        user,
    ):
        mock_classify.return_value.final_url = "https://test.com"
        mock_classify.return_value.source = Source.WEBSITE

        url = reverse("recipe_api_v1:parse-url")
        response = auth_client.post(url, {"url": "https://test.com"})

        assert response.status_code == 201

        source = RecipeSource.objects.first()
        assert source.status == StatusChoices.PROCESSING

        mock_task.assert_called_once_with(
            source.id,
            user.id,
            "https://test.com",
        )

    @patch("api.v1.recipe.repositories.recipe_repository.RecipeRepository.get_by_user_and_source")
    @patch("api.v1.recipe.services.url_classifier.UrlClassifier.classify")
    def test_user_already_has_recipe(
        self,
        mock_classify,
        mock_get_recipe,
        auth_client,
        user,
    ):
        source = RecipeSource.objects.create(
            url="https://test.com",
            status=StatusChoices.DONE,
            source=Source.WEBSITE,
        )

        mock_url_info = MagicMock()
        mock_url_info.final_url = source.url
        mock_url_info.source = Source.WEBSITE
        mock_classify.return_value = mock_url_info

        existing_recipe = Recipe.objects.create(
            created_by=user,
            source=source,
            name="Test Recipe"
        )
        mock_get_recipe.return_value = existing_recipe

        url = reverse("recipe_api_v1:parse-url")
        response = auth_client.post(url, {"url": "https://test.com"})

        assert response.status_code == 200
        assert response.data["recipe_id"] == existing_recipe.id
        assert response.data["message"] == "У вас уже есть этот рецепт"

    @patch("api.v1.recipe.views.CreateRecipeFromExistingSourceUseCase.execute")
    @patch("api.v1.recipe.views.UrlClassifier.classify")
    def test_create_from_existing_done_source(
        self,
        mock_classify,
        mock_usecase,
        auth_client,
        user,
    ):
        mock_classify.return_value.final_url = "https://test.com"
        mock_classify.return_value.source = Source.WEBSITE

        RecipeSource.objects.create(
            url="https://test.com",
            status=StatusChoices.DONE,
            source=Source.WEBSITE,
        )

        mock_usecase.return_value = type("obj", (), {"id": 42})

        url = reverse("recipe_api_v1:parse-url")
        response = auth_client.post(url, {"url": "https://test.com"})

        assert response.status_code == 201
        assert response.data["recipe_id"] == 42

    @patch("api.v1.recipe.views.UrlClassifier.classify")
    def test_processing_returns_202(
        self,
        mock_classify,
        auth_client,
    ):
        mock_classify.return_value.final_url = "https://test.com"
        mock_classify.return_value.source = Source.WEBSITE

        RecipeSource.objects.create(
            url="https://test.com",
            status=StatusChoices.PROCESSING,
            source=Source.WEBSITE,
        )

        url = reverse("recipe_api_v1:parse-url")
        response = auth_client.post(url, {"url": "https://test.com"})

        assert response.status_code == 202
