import re

from recipe.choices import MealType, Unit

"""
Константы с CSS селекторами для парсинга рецептов
"""

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

# Строки-заголовки, которые не являются ингредиентами — фильтруются при парсинге
INGREDIENT_NOISE_WORDS = {
    "продукты", "ингредиенты", "ingredients", "состав",
    "для теста", "для начинки", "для соуса", "для маринада",
    "для глазури", "для подачи", "для украшения",
}

UNIT_SYNONYMS = {
    # --- без количества ---
    "по вкусу": Unit.TO_TASTE,
    "to taste": Unit.TO_TASTE,
    "pinch": Unit.TO_TASTE,
    "a pinch": Unit.TO_TASTE,
    "handful": Unit.TO_TASTE,
    "пучок": Unit.TO_TASTE,
    "небольшой пучок": Unit.TO_TASTE,
    "щепотка": Unit.TO_TASTE,

    # --- штуки ---
    "шт": Unit.PC,
    "шт.": Unit.PC,
    "piece": Unit.PC,
    "pieces": Unit.PC,
    "pc": Unit.PC,
    "clove": Unit.PC,
    "cloves": Unit.PC,
    "зубчик": Unit.PC,
    "зубчика": Unit.PC,
    "зубчиков": Unit.PC,
    "слайса": Unit.PC,
    "слайс": Unit.PC,
    "slice": Unit.PC,
    "slices": Unit.PC,
    # описательные штучные единицы
    "веточка": Unit.PC,
    "веточки": Unit.PC,
    "веточек": Unit.PC,
    "листик": Unit.PC,
    "листика": Unit.PC,
    "листиков": Unit.PC,
    "лист": Unit.PC,
    "листа": Unit.PC,
    "листьев": Unit.PC,
    "головка": Unit.PC,
    "головки": Unit.PC,
    "головок": Unit.PC,
    "стебель": Unit.PC,
    "стебля": Unit.PC,
    "стеблей": Unit.PC,

    # --- масса ---
    "г": Unit.GR,
    "гр": Unit.GR,
    "гр.": Unit.GR,
    "g": Unit.GR,
    "gr": Unit.GR,
    "gram": Unit.GR,
    "grams": Unit.GR,
    # русские словесные формы граммов
    "грамм": Unit.GR,
    "граммов": Unit.GR,
    "грамма": Unit.GR,
    "кг": Unit.KG,
    "kg": Unit.KG,
    "kilogram": Unit.KG,
    "kilograms": Unit.KG,
    # русские словесные формы килограммов
    "килограмм": Unit.KG,
    "килограммов": Unit.KG,
    "килограмма": Unit.KG,
    "lb": Unit.GR,
    "lbs": Unit.GR,
    "pound": Unit.GR,
    "pounds": Unit.GR,
    "oz": Unit.GR,
    "ounce": Unit.GR,
    "ounces": Unit.GR,

    # --- объем ---
    "мл": Unit.ML,
    "мл.": Unit.ML,
    "ml": Unit.ML,
    "миллилитр": Unit.ML,
    "миллилитров": Unit.ML,
    "миллилитра": Unit.ML,
    "л": Unit.L,
    "l": Unit.L,
    "liter": Unit.L,
    "liters": Unit.L,
    "литр": Unit.L,
    "литра": Unit.L,
    "литров": Unit.L,
    "cup": Unit.CUP,
    "cups": Unit.CUP,
    "стакан": Unit.CUP,
    "стакана": Unit.CUP,
    "стаканов": Unit.CUP,
    "ст": Unit.CUP,
    "ст.": Unit.CUP,

    # чайная ложка — все варианты
    "tsp": Unit.TSP,
    "teaspoon": Unit.TSP,
    "teaspoons": Unit.TSP,
    "ч.л.": Unit.TSP,
    "ч.л": Unit.TSP,
    "ч л": Unit.TSP,
    "ч. л.": Unit.TSP,
    "ч. л": Unit.TSP,
    "ч. ложка": Unit.TSP,
    "ч. ложки": Unit.TSP,
    "ч. ложек": Unit.TSP,
    "чайная ложка": Unit.TSP,
    "чайной ложки": Unit.TSP,
    "чайных ложки": Unit.TSP,
    "чайных ложек": Unit.TSP,

    # столовая ложка — все варианты
    "tbsp": Unit.TBSP,
    "tablespoon": Unit.TBSP,
    "tablespoons": Unit.TBSP,
    "ст.л.": Unit.TBSP,
    "ст.л": Unit.TBSP,
    "ст л": Unit.TBSP,
    "ст. л.": Unit.TBSP,
    "ст. л": Unit.TBSP,
    "ст. ложка": Unit.TBSP,
    "ст. ложки": Unit.TBSP,
    "ст. ложек": Unit.TBSP,
    "столовая ложка": Unit.TBSP,
    "столовой ложки": Unit.TBSP,
    "столовых ложки": Unit.TBSP,
    "столовых ложек": Unit.TBSP,
}

UNIT_KEYS = sorted(UNIT_SYNONYMS.keys(), key=len, reverse=True)

AMOUNT_UNIT_RE = re.compile(
    rf"""
    (?P<amount>\d+(?:[.,]\d+)?|\d+\s+\d+/\d+|\d+/\d+)
    \s*[-–]?\s*
    (?P<unit>{'|'.join(map(re.escape, UNIT_KEYS))})
    \b
    \.?
    """,
    re.IGNORECASE | re.VERBOSE
)

# "1банан", "2яйца" — число слитно с названием
AMOUNT_PREFIX_RE = re.compile(
    r"^(\d+(?:[.,]\d+)?(?:/\d+)?|\d+\s+\d+/\d+)\s*([а-яёa-z][а-яёa-z\s\-]*)",
    re.IGNORECASE,
)

# "молоко 200" — число в конце строки без единицы
AMOUNT_SUFFIX_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*$")

RANGE_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*[-–]\s*(\d+(?:[.,]\d+)?)")

# Единица без числа — используется после вырезания диапазона
UNIT_ONLY_RE = re.compile(
    rf"(?P<unit>{'|'.join(map(re.escape, UNIT_KEYS))})\b\.?",
    re.IGNORECASE
)

CONVERSION = {
    "oz": 28.3495,
    "ounce": 28.3495,
    "ounces": 28.3495,
    "lb": 453.592,
    "lbs": 453.592,
    "pound": 453.592,
    "pounds": 453.592,
}

MEAL_TYPE_SYNONYMS = {
    "завтрак": MealType.BREAKFAST,
    "утром": MealType.BREAKFAST,
    "на завтрак": MealType.BREAKFAST,
    "breakfast": MealType.BREAKFAST,
    "morning": MealType.BREAKFAST,

    "обед": MealType.LUNCH,
    "на обед": MealType.LUNCH,
    "lunch": MealType.LUNCH,

    "ужин": MealType.DINNER,
    "на ужин": MealType.DINNER,
    "dinner": MealType.DINNER,
    "supper": MealType.DINNER,

    "суп": MealType.SOUP,
    "супчик": MealType.SOUP,
    "борщ": MealType.SOUP,
    "щи": MealType.SOUP,
    "уха": MealType.SOUP,
    "soup": MealType.SOUP,
    "stew": MealType.SOUP,       
    "chowder": MealType.SOUP,
    "bisque": MealType.SOUP,

    "десерт": MealType.DESSERT,
    "сладкое": MealType.DESSERT,
    "сладости": MealType.DESSERT,
    "dessert": MealType.DESSERT,
    "sweet": MealType.DESSERT,
    "sweets": MealType.DESSERT,

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

    "детское": MealType.BABY_FOOD,
    "детское питание": MealType.BABY_FOOD,
    "baby": MealType.BABY_FOOD,
    "baby food": MealType.BABY_FOOD,
    "kids": MealType.BABY_FOOD,
    "kids food": MealType.BABY_FOOD,

    "перекус": MealType.SNACK,
    "snack": MealType.SNACK,
    "snacks": MealType.SNACK,

    "side dish": MealType.SIDE_DISH,
    "side": MealType.SIDE_DISH,
    "side item": MealType.SIDE_DISH,
    "side order": MealType.SIDE_DISH,
    "accompaniment": MealType.SIDE_DISH,
}