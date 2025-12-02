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