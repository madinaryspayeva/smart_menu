from abc import ABC, abstractmethod

from api.v1.recipe.dto.recipe_dto import RecipeDTO


class IRecipeParserService(ABC):
    @abstractmethod
    def parse(self, url:str) -> RecipeDTO: 
        pass


class IRecipeRepository(ABC):
    @abstractmethod
    def save(self, recipe_source_id: str, user_id: str, dto: RecipeDTO): 
        pass


class IRecipeBuilderService(ABC):
    @abstractmethod
    def build(self, dto: RecipeDTO) -> RecipeDTO:
        pass