from dataclasses import asdict

from api.v1.recipe.dto.recipe_dto import IngredientDTO, RecipeDTO, StepDTO

class RecipeMapper:

    @staticmethod
    def dto_to_dict(dto: RecipeDTO) -> dict:
        return asdict(dto)
    
    @staticmethod
    def dict_to_dto(data: dict) -> RecipeDTO:
        return RecipeDTO(
            title=data.get("title"),
            description=data.get("description"),
            meal_type=data.get("meal_type"),
            tips=data.get("tips"),
            thumbnail=data.get("thumbnail"),
            ingredients=[
                IngredientDTO(**ing)
                for ing in data.get("ingredients", [])
            ],
            steps=[
                StepDTO(**step)
                for step in data.get("steps", [])
            ],
        )        
