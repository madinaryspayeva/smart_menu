from dataclasses import dataclass


@dataclass
class IngredientDTO:
    name: str | None = None
    amount: float | None = None
    unit: str | None = None
    raw: str | None = None


@dataclass
class StepDTO:
    step: str


@dataclass
class RecipeDTO:
    title: str
    description: str | None
    meal_type: str | None
    ingredients: list[IngredientDTO]
    steps: list[StepDTO]
    tips: str | None
    thumbnail: str | None = None
