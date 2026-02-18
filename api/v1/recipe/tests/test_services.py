import json
from bs4 import BeautifulSoup
from django.forms import ValidationError
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.files.base import ContentFile
from requests import RequestException
from api.v1.recipe.dto.recipe_dto import IngredientDTO, RecipeDTO, StepDTO
from api.v1.recipe.services.image_service import ImageService
from api.v1.recipe.services.llm import LLMService
from api.v1.recipe.services.url_classifier import UrlInfo
from api.v1.recipe.services.video_parser import VideoParserService
from recipe.choices import ContentType, MealType, Source, Unit


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


class TestLLMService:

    @patch("api.v1.recipe.services.llm.ollama.Client")
    @patch("api.v1.recipe.services.llm.repair_json")
    def test_extract_recipe_success(self, mock_repair_json, mock_client_cls):

        fake_content = json.dumps({
            "title": "Тестовый рецепт",
            "description": "Описание рецепта",
            "meal_type": MealType.BREAKFAST,
            "ingredients": [{"raw": "1 яблоко"}, {"raw": "2 яйца"}],
            "steps": [{"step": "Порезать яблоко"}, {"step": "Взбить яйца"}],
            "tips": "Лучше использовать свежие ингредиенты",
            "thumbnail": "http://example.com/image.jpg"
        })

        mock_client = MagicMock()
        mock_client.chat.return_value = {"message": {"content": fake_content}}
        mock_client_cls.return_value = mock_client

        mock_repair_json.return_value = fake_content

        service = LLMService()
        recipe_dto = service.extract_recipe("Некоторый текст видео")

        assert isinstance(recipe_dto, RecipeDTO)
        assert recipe_dto.title == "Тестовый рецепт"
        assert recipe_dto.description == "Описание рецепта"
        assert recipe_dto.meal_type == MealType.BREAKFAST
        assert recipe_dto.tips == "Лучше использовать свежие ингредиенты"
        assert recipe_dto.thumbnail == "http://example.com/image.jpg"

        assert len(recipe_dto.ingredients) == 2
        assert all(isinstance(i, IngredientDTO) for i in recipe_dto.ingredients)
        assert recipe_dto.ingredients[0].raw == "1 яблоко"

        assert len(recipe_dto.steps) == 2
        assert all(isinstance(s, StepDTO) for s in recipe_dto.steps)
        assert recipe_dto.steps[0].step == "Порезать яблоко"

        mock_client.chat.assert_called_once()
        mock_repair_json.assert_called_once_with(fake_content)
    
    def test_extract_json_with_backticks(self):

        service = LLMService()
        content = "```json {\"key\": \"value\"}```"
        result = service._extract_json(content)
        assert result == '{"key": "value"}'

        content2 = "``` {\"key\": 1}```"
        result2 = service._extract_json(content2)
        assert result2 == '{"key": 1}'

        content3 = '{"key": 2}'
        result3 = service._extract_json(content3)
        assert result3 == '{"key": 2}'


class TestUrlClassifier:

    @pytest.mark.parametrize(
        "url,expected_source,expected_type",
        [
            ("https://www.instagram.com/reel/ABC123", Source.INSTAGRAM, ContentType.INSTAGRAM_REEL),
            ("https://instagram.com/p/XYZ456", Source.INSTAGRAM, ContentType.INSTAGRAM_POST),
            ("https://instagram.com/somepage", Source.INSTAGRAM, ContentType.UNKNOWN),
            ("https://www.tiktok.com/@user/video/123", Source.TIKTOK, ContentType.TIKTOK_VIDEO),
            ("https://youtube.com/watch?v=abc", Source.YOUTUBE, ContentType.YOUTUBE_VIDEO),
            ("https://youtube.com/shorts/abc", Source.YOUTUBE, ContentType.YOUTUBE_SHORTS),
            ("https://youtu.be/xyz", Source.YOUTUBE, ContentType.YOUTUBE_VIDEO),
            ("https://myblog.com/recipe", Source.WEBSITE, ContentType.ARTICLE_OR_RECIPE),
        ]
    )
    def test_classify_urls(self, classifier, url, expected_source, expected_type):
        info: UrlInfo = classifier.classify(url)
        assert info.source == expected_source
        assert info.content_type == expected_type
        assert info.final_url  
        assert info.domain 

    @patch("api.v1.recipe.services.url_classifier.requests.head")
    def test_redirect_domains(self, mock_head, classifier):
        # Мок для редиректа TikTok URL
        mock_response = Mock()
        mock_response.url = "https://www.tiktok.com/@user/video/redirected"
        mock_head.return_value = mock_response

        url = "https://vm.tiktok.com/ABC123"
        info = classifier.classify(url)

        # Проверяем что _resolve_redirects вернул мокнутый URL
        assert info.final_url == "https://www.tiktok.com/@user/video/redirected"
        assert info.source == Source.TIKTOK

    def test_unknown_input(self, classifier):
        info = classifier.classify(None)
        assert info.source == Source.UNKNOWN
        assert info.content_type == ContentType.UNKNOWN
        assert info.final_url == ""
        assert info.domain == ""

    @patch("api.v1.recipe.services.url_classifier.requests.head")
    def test_request_exception_returns_original_url(self, mock_head, classifier):
        # Мок выбрасывает RequestException
        from requests.exceptions import RequestException
        mock_head.side_effect = RequestException("Connection error")

        url = "https://vm.tiktok.com/ABC123"
        info = classifier.classify(url)

        # Если запрос упал, возвращается оригинальный URL
        assert info.final_url == url
        assert info.source == Source.TIKTOK
        assert info.content_type == ContentType.TIKTOK_VIDEO

    @pytest.mark.parametrize(
        "domain_input,expected_normalized",
        [
            ("WWW.Example.com", "example.com"),
            ("www.test.org", "test.org"),
            ("MySite.com", "mysite.com"),
        ]
    )
    def test_normalize_domain(self, classifier, domain_input, expected_normalized):
        result = classifier._normalize_domain(domain_input)
        assert result == expected_normalized


class TestVideoParserService:

    @patch("api.v1.recipe.services.video_parser.yt_dlp.YoutubeDL")
    @patch("api.v1.recipe.services.video_parser.os.path.exists", return_value=True)
    @patch("api.v1.recipe.services.video_parser.os.remove")
    @patch.object(VideoParserService, "get_model")
    def test_parse_success(self, mock_model, mock_remove, mock_exists, mock_ydl, video_parser):
  
        mock_ydl_instance = mock_ydl.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.return_value = {
            "description": "Video description",
            "thumbnail": "http://example.com/thumb.jpg",
            "requested_downloads": [{"filepath": "/tmp/audio.mp3"}]
        }

        mock_transcription = MagicMock()
        mock_transcription.transcribe.return_value = ([MagicMock(text="Hello world")], None)
        mock_model.return_value = mock_transcription

        url = "http://youtube.com/fakevideo"
        result = video_parser.parse(url)

        assert isinstance(result, RecipeDTO)
        assert "Video description" in result.description
        assert "Hello world" in result.description
        assert result.thumbnail == "http://example.com/thumb.jpg"

        mock_remove.assert_called_with("/tmp/audio.mp3")

    @patch("api.v1.recipe.services.video_parser.os.path.exists", return_value=False)
    def test_parse_missing_audio(self, mock_exists, video_parser):
        with pytest.raises(FileNotFoundError):
            video_parser.parse("http://youtube.com/fakevideo")

    @patch("api.v1.recipe.services.video_parser.yt_dlp.YoutubeDL")
    def test_extract_audio_and_description(self, mock_ydl, video_parser):

        mock_ydl_instance = mock_ydl.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.return_value = {
            "description": "desc",
            "thumbnail": "thumb",
            "requested_downloads": [{"filepath": "/tmp/audio.mp3"}]
        }

        audio_path, desc, thumb = video_parser._extract_audio_and_description("url")
        assert audio_path == "/tmp/audio.mp3"
        assert desc == "desc"
        assert thumb == "thumb"

    def test_transcribe_audio_calls_model(self, video_parser):

        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([MagicMock(text="text")], None)

        with patch.object(VideoParserService, "get_model", return_value=mock_model):
            text = video_parser._transcribe_audio("/tmp/audio.mp3")
            assert "text" in text


class TestWebParserService:

    @patch("api.v1.recipe.services.web_parser.requests.Session.get")
    def test_parse_success_with_json_ld(self, mock_get, web_parser):
        html = """
        <html>
            <script type="application/ld+json">
            {
                "@type": "Recipe",
                "name": "Pancakes",
                "recipeIngredient": ["1 egg", "200 ml milk"],
                "recipeInstructions": [
                    {"text": "Mix"},
                    {"text": "Cook"}
                ],
                "image": "http://example.com/img.jpg"
            }
            </script>
        </html>
        """

        mock_response = MagicMock()
        mock_response.content = html.encode()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = web_parser.parse("http://example.com")

        assert isinstance(result, RecipeDTO)
        assert result.title == "Pancakes"
        assert len(result.ingredients) == 2
        assert result.ingredients[0].raw == "1 egg"
        assert len(result.steps) == 2
        assert result.thumbnail == "http://example.com/img.jpg"


    @patch("api.v1.recipe.services.web_parser.requests.Session.get")
    @patch("api.v1.recipe.services.web_parser.selectors")
    def test_parse_fallback_selectors(self, mock_selectors, mock_get, web_parser):

        html = """
        <html>
            <h1 class="title">Soup</h1>
            <ul class="ingredients">
                <li><span>Water</span></li>
                <li><span>Salt</span></li>
            </ul>
            <div class="instructions">
                <p>Boil water</p>
                <p>Add salt</p>
            </div>
            <img class="recipe-img" src="image.jpg"/>
        </html>
        """

        mock_selectors.TITLE_SELECTORS = [".title"]
        mock_selectors.INGREDIENTS_SELECTORS = [".ingredients li"]
        mock_selectors.INSTRUCTIONS_SELECTORS = [".instructions"]
        mock_selectors.COOK_TIME_SELECTORS = []
        mock_selectors.SERVINGS_SELECTORS = []
        mock_selectors.IMAGE_SELECTORS = [".recipe-img"]
        mock_selectors.STRUCTURED_DATA_SELECTORS = []

        mock_response = MagicMock()
        mock_response.content = html.encode()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = web_parser.parse("http://example.com")

        assert result.title == "Soup"
        assert len(result.ingredients) == 2
        assert result.ingredients[0].raw == "Water"
        assert len(result.steps) == 2
        assert result.thumbnail == "image.jpg"


    def test_extract_structured_data_invalid_json(self, web_parser):
        html = """
        <script type="application/ld+json">
            { invalid json }
        </script>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = web_parser._extract_structured_data(soup)
        assert result == {}


    @patch("api.v1.recipe.services.web_parser.requests.Session.get")
    def test_parse_request_exception(self, mock_get, web_parser):
        mock_get.side_effect = RequestException("Network error")

        with pytest.raises(ValidationError) as exc:
            web_parser.parse("http://bad-url.com")

        assert "Ошибка загрузки страницы" in str(exc.value)


    @patch("api.v1.recipe.services.web_parser.requests.Session.get")
    def test_parse_generic_exception(self, mock_get, web_parser):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("Unexpected")
        mock_get.return_value = mock_response

        with pytest.raises(ValidationError) as exc:
            web_parser.parse("http://error.com")

        assert "Ошибка парсинга" in str(exc.value)


    def test_parse_structured_recipe_variants(self, web_parser):
        data = {
            "@type": "Recipe",
            "headline": "Alt Title",
            "recipeIngredient": ["Salt", "Pepper"],
            "recipeInstructions": ["Step 1", "Step 2"],
            "image": [{"url": "http://img.jpg"}],
            "cookTime": "PT30M",
            "recipeYield": "4 servings"
        }

        result = web_parser._parse_structured_recipe(data)

        assert result["title"] == "Alt Title"
        assert len(result["ingredients"]) == 2
        assert len(result["steps"]) == 2
        assert result["thumbnail"] == "http://img.jpg"
        assert result["cook_time"] == "PT30M"
        assert result["servings"] == "4 servings"


    def test_find_list_by_selectors(self, web_parser):
        html = """
        <ul class="ingredients">
            <li><span>Flour</span></li>
            <li><span>Sugar</span></li>
        </ul>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = web_parser._find_list_by_selectors(soup, [".ingredients li"])
        assert result == ["Flour", "Sugar"]


    def test_find_steps(self, web_parser):
        html = """
        <div class="steps">
            <p>Step one</p>
            <p>Step two</p>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = web_parser._find_steps(soup, [".steps"])
        assert result == ["Step one", "Step two"]


    def test_find_image(self, web_parser):
        html = '<img class="recipe" src="photo.jpg"/>'
        soup = BeautifulSoup(html, "html.parser")

        import api.v1.recipe.constants as selectors
        selectors.IMAGE_SELECTORS = [".recipe"]

        result = web_parser._find_image(soup)
        assert result == "photo.jpg"


    def test_clean_text(self, web_parser):
        text = "  Hello   \n world   "
        assert web_parser._clean_text(text) == "Hello world"


class TestRecipeBuilderService:

    def test_build_normalizes_ingredients(self, builder):
        dto = RecipeDTO(
            title="Test",
            description="",
            meal_type=None,
            ingredients=[IngredientDTO(raw="100 g sugar")],
            steps=[],
            tips=None,
            thumbnail=None,
        )

        with patch("api.v1.recipe.services.recipe_builder.UnitConverter.convert",
                   return_value=(100.0, Unit.GR.value)):
            result = builder.build(dto)

        assert result.ingredients[0].amount == 100.0
        assert result.ingredients[0].unit == Unit.GR.value

    @pytest.mark.parametrize(
        "title,expected",
        [
            ("Best breakfast ever", MealType.BREAKFAST.value),
            ("Healthy dinner salad", MealType.DINNER.value),
            ("Quick lunch sandwich", MealType.LUNCH.value),
        ],
    )
    def test_parse_meal_type_from_title(self, builder, title, expected):
        dto = RecipeDTO(
            title=title,
            description="",
            meal_type=None,
            ingredients=[],
            steps=[],
            tips=None,
            thumbnail=None,
        )

        result = builder._parse_meal_type(dto)

        assert result == expected

    def test_parse_meal_type_none(self, builder):
        dto = RecipeDTO(
            title="Something random",
            description="No keywords",
            meal_type=None,
            ingredients=[],
            steps=[],
            tips=None,
            thumbnail=None,
        )

        result = builder._parse_meal_type(dto)
        assert result is None

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("150", 150.0),
            ("1,5", 1.5),
            ("1.5", 1.5),
            ("1/2", 0.5),
            ("1 1/2", 1.5),
        ]
    )
    def test_parse_amount(self, builder, text, expected):
        assert builder._parse_amount(text) == expected

    def test_parse_amount_invalid(self, builder):
        assert builder._parse_amount("abc") is None

    def test_parse_ingredient_simple(self, builder):
        ingredient = IngredientDTO(raw="200 g flour")

        with patch("api.v1.recipe.services.recipe_builder.UnitConverter.convert",
                   return_value=(200.0, Unit.GR.value)):
            result = builder._parse_ingredient(ingredient)

        assert result.amount == 200.0
        assert result.unit == Unit.GR.value
        assert "flour" in result.name

    def test_parse_ingredient_range(self, builder):
        ingredient = IngredientDTO(raw="100-200 g sugar")

        with patch("api.v1.recipe.services.recipe_builder.UnitConverter.convert",
                   return_value=(150.0, Unit.GR.value)):
            result = builder._parse_ingredient(ingredient)

        assert result.amount == 150.0

    def test_parse_ingredient_to_taste(self, builder):
        ingredient = IngredientDTO(raw="salt to taste")

        result = builder._parse_ingredient(ingredient)

        assert result["unit"] == Unit.TO_TASTE.value
        assert result["amount"] is None

    def test_parse_ingredient_without_amount(self, builder):
        ingredient = IngredientDTO(raw="flour")

        result = builder._parse_ingredient(ingredient)

        assert result.amount is None
        assert result.unit is None
        assert result.name == "flour"

    def test_unit_converter_called(self, builder):
        ingredient = IngredientDTO(raw="1 kg rice")

        with patch("api.v1.recipe.services.recipe_builder.UnitConverter.convert",
                   return_value=(1000.0, Unit.GR.value)) as mock_convert:
            builder._parse_ingredient(ingredient)

        mock_convert.assert_called()
