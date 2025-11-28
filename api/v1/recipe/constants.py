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

PREP_TIME_SELECTORS = [
    '[class*="prep-time"]',
    '.wprm-recipe-prep_time', 
    '[itemprop="prepTime"]',
    '.tasty-recipes-prep-time',
    '.prep-time'
]

COOK_TIME_SELECTORS = [
    '[class*="cook-time"]',
    '.wprm-recipe-cook_time',
    '[itemprop="cookTime"]', 
    '.tasty-recipes-cook-time',
    '.cook-time'
]

SERVINGS_SELECTORS = [
    '[class*="serving"]',
    '.wprm-recipe-servings',
    '[itemprop="recipeYield"]',
    '.tasty-recipes-yield',
    '.recipe-servings',
    '.servings'
]

IMAGE_SELECTORS = [
    '.recipe-image img',
    '.recipe-img img', 
    '.wp-post-image',
    '[itemprop="image"]',
    '.wprm-recipe-image img',
    'img.recipe-photo'
]

INGREDIENTS_SELECTORS = [
    '.ingredients li',
    '.recipe-ingredients li',
    '.wprm-recipe-ingredient',
    '.tasty-recipes-ingredients li',
    '[itemprop="recipeIngredient"]',
    '.ingredient-list li',
    'ul.ingredients li'
]

INSTRUCTIONS_SELECTORS = [
    '.instructions li', 
    '.recipe-steps li',
    '.wprm-recipe-instruction',
    '.tasty-recipes-instructions li',
    '[itemprop="recipeInstructions"]',
    '.direction-list li',
    'ol.instructions li'
]