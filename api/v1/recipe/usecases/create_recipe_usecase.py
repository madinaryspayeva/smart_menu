from dataclasses import asdict
from api.v1.recipe.dto.recipe_dto import RecipeDTO
from api.v1.recipe.interfaces.recipe_parser import IRecipeBuilderService, IRecipeParserService, IRecipeRepository


class CreateRecipeUseCase:
    """
    Usecase для создания рецепта из RecipeSource
    """

    def __init__(
            self,
            parser: IRecipeParserService,
            repository: IRecipeRepository,
            builder: IRecipeBuilderService,
    ):
        self.parser = parser
        self.repository = repository
        self.builder = builder
    

    def execute(self, source_id: str, user_id: str, source: str):

        dto = self.parser.parse(source)
        
        normalize_dto = self.builder.build(dto)

        return self.repository.save(
            recipe_source_id=source_id,
            user_id=user_id,
            dto=normalize_dto
        )

        
