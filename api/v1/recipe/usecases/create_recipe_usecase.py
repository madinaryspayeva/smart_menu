from api.v1.recipe.interfaces.recipe_parser import (
    IRecipeBuilderService,
    IRecipeParserService,
    IRecipeRepository,
)
from api.v1.recipe.interfaces.uow import IUnitOfWork
from api.v1.recipe.mappers.recipe_mapper import RecipeMapper
from api.v1.recipe.services.llm import LLMService


class CreateRecipeUseCase:
    """
    Универсальный usecase для создания рецепта из любого источника.
    Если передан llm — используется для обработки необработанного текста (для видео).
    """

    def __init__(
            self,
            parser: IRecipeParserService,
            repository: IRecipeRepository,
            builder: IRecipeBuilderService,
            uow: IUnitOfWork,
            llm: LLMService | None = None
    ):
        self.parser = parser
        self.repository = repository
        self.builder = builder
        self.uow = uow
        self.llm = llm
    

    def execute(self, source_id: str, user_id: str, url: str):

        if self.repository.exists_for_user(source_id, user_id): 
            return self.repository.get_by_user_and_source(source_id, user_id)
        
        raw_data = self.parser.parse(url)

        if self.llm:
            dto = self.llm.extract_recipe(raw_data.description)
            dto.thumbnail = raw_data.thumbnail
        else:
            dto = raw_data
        
        final_dto = self.builder.build(dto)

        with self.uow:
            parsed_dict = RecipeMapper.dto_to_dict(final_dto)
            self.repository.update_source_parsed_data(source_id, parsed_dict)
            recipe = self.repository.save(source_id, user_id, final_dto)
        
        return recipe


class CreateRecipeFromExistingSourceUseCase:
    """
    Usecase для создания рецепта из существующего RecipeSource
    """

    def __init__(self, repository: IRecipeRepository):
        self.repository = repository
    
    def execute(self, user_id: str, source_id: str):
        parsed_dict = self.repository.get_parsed_data_from_source(source_id)
        
        dto = RecipeMapper.dict_to_dto(parsed_dict)

        return self.repository.create_from_dto(dto, user_id, source_id)
