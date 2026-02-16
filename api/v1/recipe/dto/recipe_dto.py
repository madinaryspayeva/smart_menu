from dataclasses import dataclass
from typing import List, Optional


@dataclass
class IngredientDTO:
    raw: Optional[str]
    name: str
    amount: Optional[float]
    unit: Optional[str]


@dataclass
class StepDTO:
    step: str


@dataclass
class RecipeDTO:
    title: str
    description: Optional[str]
    meal_type: Optional[str]
    ingredients: List[IngredientDTO]
    steps: List[StepDTO]
    tips: Optional[str]
    thumbnail: Optional[str] = None