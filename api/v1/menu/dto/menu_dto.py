from dataclasses import dataclass
from datetime import date


@dataclass
class MenuEntryDTO:
    date: date
    meal_type: str
    recipe_id: str
    servings: int


@dataclass
class CreateMenuDTO:
    name: str
    servings: int
    dates: list[date]
    meal_types: list[str]
    entries: list[MenuEntryDTO] | None = None


@dataclass
class ShoppingItemDTO:
    product_name: str
    product_id: str
    category: str
    quantity: float
    unit: str