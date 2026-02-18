import pytest
from unittest.mock import Mock, MagicMock, patch

from api.v1.recipe.usecases.create_recipe_usecase import CreateRecipeFromExistingSourceUseCase, CreateRecipeUseCase


class TestCreateRecipeUseCase:

    @patch("api.v1.recipe.mappers.recipe_mapper.RecipeMapper.dto_to_dict")
    def test_returns_existing_recipe_if_already_exists(self, mock_mapper):
        parser = Mock()
        repository = Mock()
        builder = Mock()
        uow = MagicMock()
        llm = None

        existing_recipe = Mock()

        repository.exists_for_user.return_value = True
        repository.get_by_user_and_source.return_value = existing_recipe

        usecase = CreateRecipeUseCase(parser, repository, builder, uow, llm)

        result = usecase.execute("source1", "user1", "url")

        repository.get_by_user_and_source.assert_called_once_with("source1", "user1")
        parser.parse.assert_not_called()
        assert result == existing_recipe

    @patch("api.v1.recipe.mappers.recipe_mapper.RecipeMapper.dto_to_dict")
    def test_execute_without_llm(self, mock_mapper):
        parser = Mock()
        repository = Mock()
        builder = Mock()
        uow = MagicMock()
        llm = None

        raw_data = Mock()
        final_dto = Mock()
        recipe = Mock()

        repository.exists_for_user.return_value = False
        parser.parse.return_value = raw_data
        builder.build.return_value = final_dto
        repository.save.return_value = recipe
        mock_mapper.return_value = {"title": "test"}

        usecase = CreateRecipeUseCase(parser, repository, builder, uow, llm)

        result = usecase.execute("source1", "user1", "url")

        parser.parse.assert_called_once_with("url")
        builder.build.assert_called_once_with(raw_data)
        mock_mapper.assert_called_once_with(final_dto)
        repository.update_source_parsed_data.assert_called_once()
        repository.save.assert_called_once_with("source1", "user1", final_dto)
        assert result == recipe

    @patch("api.v1.recipe.mappers.recipe_mapper.RecipeMapper.dto_to_dict")
    def test_execute_with_llm(self, mock_mapper):
        parser = Mock()
        repository = Mock()
        builder = Mock()
        uow = MagicMock()
        llm = Mock()

        raw_data = Mock()
        raw_data.description = "raw text"
        raw_data.thumbnail = "thumb.jpg"

        dto_from_llm = Mock()
        final_dto = Mock()
        recipe = Mock()

        repository.exists_for_user.return_value = False
        parser.parse.return_value = raw_data
        llm.extract_recipe.return_value = dto_from_llm
        builder.build.return_value = final_dto
        repository.save.return_value = recipe
        mock_mapper.return_value = {"title": "test"}

        usecase = CreateRecipeUseCase(parser, repository, builder, uow, llm)

        result = usecase.execute("source1", "user1", "url")

        llm.extract_recipe.assert_called_once_with("raw text")
        builder.build.assert_called_once_with(dto_from_llm)
        repository.save.assert_called_once()
        assert result == recipe

    @patch("api.v1.recipe.mappers.recipe_mapper.RecipeMapper.dto_to_dict")
    def test_execute_uses_uow_context_manager(self, mock_mapper):
        parser = Mock()
        repository = Mock()
        builder = Mock()
        uow = MagicMock()
        llm = None

        raw_data = Mock()
        final_dto = Mock()

        repository.exists_for_user.return_value = False
        parser.parse.return_value = raw_data
        builder.build.return_value = final_dto
        mock_mapper.return_value = {"title": "test"}

        usecase = CreateRecipeUseCase(parser, repository, builder, uow, llm)

        usecase.execute("source1", "user1", "url")

        assert uow.__enter__.called
        assert uow.__exit__.called


class TestCreateRecipeFromExistingSourceUseCase:

    @patch("api.v1.recipe.mappers.recipe_mapper.RecipeMapper.dict_to_dto")
    def test_execute_creates_recipe_from_existing_source(self, mock_mapper):
        repository = Mock()

        parsed_dict = {"title": "Test"}
        dto = Mock()
        recipe = Mock()

        repository.get_parsed_data_from_source.return_value = parsed_dict
        mock_mapper.return_value = dto
        repository.create_from_dto.return_value = recipe

        usecase = CreateRecipeFromExistingSourceUseCase(repository)

        result = usecase.execute("user1", "source1")

        repository.get_parsed_data_from_source.assert_called_once_with("source1")
        repository.create_from_dto.assert_called_once_with(dto, "user1", "source1")
        assert result == recipe
