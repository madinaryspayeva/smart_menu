import requests
import json
import re
from bs4 import BeautifulSoup

from django.core.exceptions import ValidationError

import api.v1.recipe.constants as selectors
from api.v1.recipe.dto.recipe_dto import IngredientDTO, RecipeDTO, StepDTO
from api.v1.recipe.interfaces.recipe_parser import IRecipeParserService


class WebParserService(IRecipeParserService):
    """
    Сервис для парсинга рецептов с сайтов
    """

    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def parse(self, url: str) -> RecipeDTO:
        """
        Основной метод - парсит рецепт по URL и возвращает RecipeDTO
        """
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.content, "html.parser")

            recipe_data = self._parse_recipe_data(soup, url)

            ingredients = [
                IngredientDTO(raw=i["raw"], name=None, amount=None, unit=None)
                for i in recipe_data.get("ingredients", [])
            ]
            steps = [
                StepDTO(step=s["step"])
                for s in recipe_data.get("steps", [])
            
            ]

            return RecipeDTO(
                title=recipe_data.get("title"),
                description=recipe_data.get("description"),
                meal_type=recipe_data.get("meal_type"),
                ingredients=ingredients,
                steps=steps,
                tips=recipe_data.get("tips"),
                thumbnail=recipe_data.get("thumbnail")
            )
        
        except requests.RequestException as e:
            raise ValidationError(f"Ошибка загрузки страницы: {e}")
        except Exception as e:
            raise ValidationError(f"Ошибка парсинга: {e}")
    
    def _parse_recipe_data(self, soup, url):
        """
        Парсит данные рецепта из HTML
        """
        result = {
            "source_url": url,
            "title": None,
            "ingredients": [],
            "steps": [],
            "cook_time": None,
            "servings": None,
            "thumbnail": None,
        } 

        # 1. Пробуем структурированные данные (JSON-LD)
        structured_data = self._extract_structured_data(soup)
        if structured_data:
            result.update(structured_data)
        
         # 2. Если структурированных данных нет, парсим по селекторам
        if not result["title"]:
            result["title"] = self._find_by_selectors(soup, selectors.TITLE_SELECTORS)
        
        if not result['ingredients']:
            ingredients = self._find_list_by_selectors(soup, selectors.INGREDIENTS_SELECTORS)
            result['ingredients'] = [{"raw": self._clean_text(ing)} for ing in ingredients]
        
        if not result['steps']:
            instructions = self._find_steps(soup, selectors.INSTRUCTIONS_SELECTORS)
            result['steps'] = [{"step": self._clean_text(step)} for step in instructions]
        
        if not result['cook_time']:
            result['cook_time'] = self._find_by_selectors(soup, selectors.COOK_TIME_SELECTORS)
        
        if not result['servings']:
            result['servings'] = self._find_by_selectors(soup, selectors.SERVINGS_SELECTORS)
        
        if not result['thumbnail']:
            result['thumbnail'] = self._find_image(soup)
        
        return result


    def _extract_structured_data(self, soup):
        """
        Извлекает данные из структурированной разметки (JSON-LD)
        """
        for selector in selectors.STRUCTURED_DATA_SELECTORS:
            scripts = soup.select(selector)
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        data = data[0]
                    
                    if data.get("@type") in ["Recipe", "HowTo"]:
                        return self._parse_structured_recipe(data)
                except:
                    continue
        
        return {}
    
    def _parse_structured_recipe(self, data):
        """
        Парсит структурированные данные рецепта
        """
        result = {}

        result["title"] = data.get("name") or data.get("headline")


        ingredients = data.get("recipeIngredient", [])
        if isinstance(ingredients, list):
            result["ingredients"] = [{"raw": self._clean_text(ingredient)} for ingredient in ingredients]


        instructions = data.get("recipeInstructions", [])
        if isinstance(instructions, list):
            instructions_text = []
            for step in instructions:
                if isinstance(step, dict):
                    instructions_text.append(step.get("text"))
                elif isinstance(step, str):
                    instructions_text.append(step)
            result["steps"] = [{"step": self._clean_text(step)} for step in instructions_text]


        result["cook_time"] = data.get("cookTime")


        result['servings'] = data.get('recipeYield')


        image = data.get("image")
        if isinstance(image, dict):
            result["thumbnail"] = image.get("url")
        elif isinstance(image, list) and len(image) > 0:
            result["thumbnail"] = image[0].get("url") if isinstance(image[0], dict) else image[0]
        elif isinstance(image, str):
            result["thumbnail"] = image 

        return result
    
    def _find_by_selectors(self, soup, selectors):
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return self._clean_text(element.get_text())
        return None

    
    def _find_list_by_selectors(self, soup, selectors):
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                texts = []
                for element in elements:
                    spans = element.select("span")
                    for span in spans:
                        text = self._clean_text(span.get_text())
                        if text:
                            texts.append(text)
                return texts
        return []
    
    def _find_steps(self, soup, selectors):
    
        steps = []
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                p_tags = element.select("p")
                for p in p_tags:
                    text = self._clean_text(p.get_text())
                    if text:
                        steps.append(text)
        return steps
    
    def _find_image(self, soup):
        for selector in selectors.IMAGE_SELECTORS:
            img = soup.select_one(selector)
            if img and img.get("src"):
                return img["src"]
        return None
    
    def _clean_text(self, text):
        if not text:
            return ""
        
        cleaned = re.sub(r'\s+', ' ', text.strip())
        return cleaned
