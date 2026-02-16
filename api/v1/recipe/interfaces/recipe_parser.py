from abc import ABC, abstractmethod

from api.v1.recipe.dto.recipe_dto import RecipeDTO
from recipe.models import Recipe, RecipeSource


class IRecipeParserService(ABC):
    @abstractmethod
    def parse(self, url:str) -> RecipeDTO: 
        pass


class IRecipeRepository(ABC):

    @abstractmethod
    def exists_for_user(self, source_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    def get_by_user_and_source(self, source_id: str, user_id: str) -> Recipe | None:
        pass

    @abstractmethod
    def save(self, source_id: str, user_id: str, dto: RecipeDTO): 
        pass

class IRecipeBuilderService(ABC):
    @abstractmethod
    def build(self, dto: RecipeDTO) -> RecipeDTO:
        pass