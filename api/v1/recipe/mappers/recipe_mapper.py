from dataclasses import asdict

from api.v1.recipe.dto.recipe_dto import IngredientDTO, RecipeDTO, StepDTO


class RecipeMapper:

    @staticmethod
    def dto_to_dict(dto: RecipeDTO) -> dict:
        return asdict(dto)
    
    @staticmethod
    def _normalize_tips(raw_tips) -> str | None:
        if not raw_tips:
            return None
        if isinstance(raw_tips, list):
            return "\n".join(str(t) for t in raw_tips if t)
        return str(raw_tips)

    @staticmethod
    def dict_to_dto(data: dict) -> RecipeDTO:
        return RecipeDTO(
            title=data.get("title"),
            description=data.get("description"),
            meal_type=data.get("meal_type"),
            tips=RecipeMapper._normalize_tips(data.get("tips")),
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
