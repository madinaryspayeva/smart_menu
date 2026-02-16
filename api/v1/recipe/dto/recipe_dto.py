from dataclasses import dataclass
from typing import List, Optional


@dataclass
class IngredientDTO:
    name: Optional[str] = None
    amount: Optional[float] = None
    unit: Optional[str] = None
    raw: Optional[str] = None


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
