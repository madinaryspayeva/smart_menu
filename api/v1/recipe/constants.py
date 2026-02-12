import re

from recipe.choices import MealType, Unit


"""
Константы с CSS селекторами для парсинга рецептов
"""

# Структурированные данные (JSON-LD)

STRUCTURED_DATA_SELECTORS = [
    'script[type="application/ld+json"]'
]

TITLE_SELECTORS = [
    'h1[class*="recipe-title"]',
    'h1[class*="title"]', 
    '.recipe-title',
    '.entry-title',
    '[itemprop="name"]',
    '.wprm-recipe-name',
    '.tasty-recipes-title',
    'h1' 
]

COOK_TIME_SELECTORS = [
    '[class*="cook-time"]',
    '.wprm-recipe-cook_time',
    '[itemprop="cookTime"]', 
    '.tasty-recipes-cook-time',
    '.cook-time',
]

SERVINGS_SELECTORS = [
    '[class*="serving"]',
    '.wprm-recipe-servings',
    '[itemprop="recipeYield"]',
    '.tasty-recipes-yield',
    '.recipe-servings',
    '.servings',
    '.el',
]

IMAGE_SELECTORS = [
    '.recipe-image img',
    '.recipe-img img', 
    '.wp-post-image',
    '[itemprop="image"]',
    '.wprm-recipe-image img',
    'img.recipe-photo',
    'table.main_image img',
    'table[class*="main_image"]',
    '.main_image table',
]

INGREDIENTS_SELECTORS = [
    '.ingredients li',
    '.recipe-ingredients li',
    '.wprm-recipe-ingredient',
    '.tasty-recipes-ingredients li',
    '[itemprop="recipeIngredient"]',
    '.ingredient-list li',
    'ul.ingredients li',
    'table.prod tr',
    '.prod tr',
    '.ingr',
    'table.ingredients tr',           
    'table.recipe-ingredients tr',   
    '.ingredient-table tr',          
    'tr[itemprop="recipeIngredient"]', 
]

INSTRUCTIONS_SELECTORS = [
    '.instructions li', 
    '.recipe-steps li',
    '.wprm-recipe-instruction',
    '.tasty-recipes-instructions li',
    '[itemprop="recipeInstructions"]',
    '.direction-list li',
    'ol.instructions li',
    '.stepbystep',
    '.step_n',
]


LLM_SCHEMA = """
    {
    "title": "string",
    "description": "string",
    "meal_type": "string | null",
    "ingredients": [
        {
        "raw": "string"
        }
    ],
    "steps": [
        {
        "step": "string"
        }
    ],
    "tips": ["string"]
    }
"""


UNIT_SYNONYMS = {
    # --- без количества ---
    "по вкусу": Unit.TO_TASTE,
    "to taste": Unit.TO_TASTE,
    "pinch": Unit.TO_TASTE,
    "a pinch": Unit.TO_TASTE,
    "handful": Unit.TO_TASTE,
    "пучок": Unit.TO_TASTE,
    "небольшой пучок": Unit.TO_TASTE,

    # --- штуки ---
    "шт": Unit.PC,
    "piece": Unit.PC,
    "pieces": Unit.PC,
    "шт.": Unit.PC,
    "pc": Unit.PC,
    "clove": Unit.PC,
    "cloves": Unit.PC,
    "зубчик": Unit.PC,
    "зубчика": Unit.PC,
    "слайса": Unit.PC,
    "слайс": Unit.PC,
    "slice": Unit.PC,
    "slices": Unit.PC,

    # --- масса ---
    "г": Unit.GR,
    "гр": Unit.GR,
    "гр.": Unit.GR,
    "g": Unit.GR,
    "gr": Unit.GR,
    "gram": Unit.GR,
    "grams": Unit.GR,

    "кг": Unit.KG,
    "kg": Unit.KG,
    "kilogram": Unit.KG,
    "kilograms": Unit.KG,

    "lb": Unit.KG,
    "lbs": Unit.KG,
    "pound": Unit.KG,
    "pounds": Unit.KG,

    "oz": Unit.GR,
    "ounce": Unit.GR,
    "ounces": Unit.GR,

    # --- объем ---
    "мл": Unit.ML,
    "мл.": Unit.ML,
    "ml": Unit.ML,

    "л": Unit.L,
    "l": Unit.L,
    "liter": Unit.L,
    "liters": Unit.L,

    "cup": Unit.CUP,
    "cups": Unit.CUP,
    "стакан": Unit.CUP,
    "стакана": Unit.CUP,
    "стаканов": Unit.CUP,
    "ст": Unit.CUP,
    "ст.": Unit.CUP,

    "tsp": Unit.TSP,
    "teaspoon": Unit.TSP,
    "teaspoons": Unit.TSP,
    "ч.л.": Unit.TSP,
    "ч.л": Unit.TSP,
    "ч л": Unit.TSP,

    "tbsp": Unit.TBSP,
    "tablespoon": Unit.TBSP,
    "tablespoons": Unit.TBSP,
    "ст.л.": Unit.TBSP,
    "ст.л": Unit.TBSP,
    "ст л": Unit.TBSP,
    "ст. л.": Unit.TBSP,
}

UNIT_KEYS = sorted(UNIT_SYNONYMS.keys(), key=len, reverse=True)

AMOUNT_UNIT_RE = re.compile(
    rf"""
    (?P<amount>\d+(?:[.,]\d+)?|\d+/\d+)
    \s*[-–]?\s*
    (?P<unit>{'|'.join(map(re.escape, UNIT_KEYS))})
    \b
    \.?
    """,
    re.IGNORECASE | re.VERBOSE
)

CONVERSION = {
        # масса → граммы
        "oz": 28.3495,
        "ounce": 28.3495,
        "ounces": 28.3495,

        "lb": 453.592,
        "lbs": 453.592,
        "pound": 453.592,
        "pounds": 453.592,
    }

MEAL_TYPE_SYNONYMS = {
    # BREAKFAST
    "завтрак": MealType.BREAKFAST,
    "утром": MealType.BREAKFAST,
    "на завтрак": MealType.BREAKFAST,
    "breakfast": MealType.BREAKFAST,
    "morning": MealType.BREAKFAST,

    # LUNCH
    "обед": MealType.LUNCH,
    "на обед": MealType.LUNCH,
    "lunch": MealType.LUNCH,

    # DINNER
    "ужин": MealType.DINNER,
    "на ужин": MealType.DINNER,
    "dinner": MealType.DINNER,
    "supper": MealType.DINNER,

    # SOUP 
    "суп": MealType.SOUP,
    "супчик": MealType.SOUP,
    "борщ": MealType.SOUP,
    "щи": MealType.SOUP,
    "уха": MealType.SOUP,
    "soup": MealType.SOUP,
    "stew": MealType.SOUP,       
    "chowder": MealType.SOUP,
    "bisque": MealType.SOUP,

    # DESSERT
    "десерт": MealType.DESSERT,
    "сладкое": MealType.DESSERT,
    "сладости": MealType.DESSERT,
    "dessert": MealType.DESSERT,
    "sweet": MealType.DESSERT,
    "sweets": MealType.DESSERT,

    # DRINK
    "напиток": MealType.DRINK,
    "напитки": MealType.DRINK,
    "drink": MealType.DRINK,
    "drinks": MealType.DRINK,
    "beverage": MealType.DRINK,

    "коктейль": MealType.DRINK,
    "cocktail": MealType.DRINK,

    "чай": MealType.DRINK,
    "tea": MealType.DRINK,

    "кофе": MealType.DRINK,
    "coffee": MealType.DRINK,

    # BABY FOOD
    "детское": MealType.BABY_FOOD,
    "детское питание": MealType.BABY_FOOD,
    "baby": MealType.BABY_FOOD,
    "baby food": MealType.BABY_FOOD,
    "kids": MealType.BABY_FOOD,
    "kids food": MealType.BABY_FOOD,

    # SNACK
    "перекус": MealType.SNACK,
    "snack": MealType.SNACK,
    "snacks": MealType.SNACK,

    # SIDE DISH 
    "side dish": MealType.SIDE_DISH,
    "side": MealType.SIDE_DISH,
    "side item": MealType.SIDE_DISH,
    "side order": MealType.SIDE_DISH,
    "accompaniment": MealType.SIDE_DISH,
}
