import pytest
from unittest.mock import patch, MagicMock
from django.core.files.base import ContentFile
from api.v1.recipe.services.image_service import ImageService


@pytest.mark.django_db
class TestImageService:

    @patch("api.v1.recipe.services.image_service.requests.get")
    def test_download_image_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = b"fake image bytes"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        url = "http://example.com/image.jpg"
        content, filename = ImageService.download_image(url)

        assert content == b"fake image bytes"
        assert filename.endswith(".jpg")
        mock_get.assert_called_once_with(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

    @patch("api.v1.recipe.services.image_service.requests.get")
    def test_download_image_failure(self, mock_get):
        mock_get.side_effect = Exception("Connection error")

        url = "http://example.com/image.jpg"
        content, filename = ImageService.download_image(url)

        assert content is None
        assert filename is None

    def test_save_image_to_model_saves_file(self):
        mock_field = MagicMock()
        mock_instance = MagicMock()
        setattr(mock_instance, "image", mock_field)

        image_bytes = b"fake bytes"
        filename = "test.jpg"

        ImageService.save_image_to_model(mock_instance, "image", image_bytes, filename)

        mock_field.save.assert_called_once()
        args, kwargs = mock_field.save.call_args
        assert args[0] == filename
        assert isinstance(args[1], ContentFile)
        assert kwargs["save"] is True

    def test_save_image_to_model_no_bytes(self):
        mock_field = MagicMock()
        mock_instance = MagicMock()
        setattr(mock_instance, "image", mock_field)

        result = ImageService.save_image_to_model(mock_instance, "image", None, "test.jpg")

        mock_field.save.assert_not_called()