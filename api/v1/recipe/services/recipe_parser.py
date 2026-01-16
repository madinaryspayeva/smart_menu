import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from django.core.exceptions import ValidationError

import api.v1.recipe.constants as selectors


class WebParserService:
    """
    Сервис для парсинга рецептов с сайтов
    """

    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def parse_recipe_from_url(self, url):
        """
        Основной метод - парсит рецепт по URL
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            result = self._parse_recipe_data(soup, url)

            if not result.get('title'):
                raise ValidationError("Не удалось найти название рецепта")
            if not result.get('ingredients'):
                raise ValidationError("Не удалось найти ингредиенты")
                
            return result
        
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
            "instructions": [],
            "cook_time": None,
            "servings": None,
            "image": None,
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
            result['ingredients'] = [self._clean_text(ing) for ing in ingredients]
        
        if not result['instructions']:
            instructions = self._find_list_by_selectors(soup, selectors.INSTRUCTIONS_SELECTORS)
            result['instructions'] = [self._clean_text(step) for step in instructions]
        
        if not result['cook_time']:
            result['cook_time'] = self._find_by_selectors(soup, selectors.COOK_TIME_SELECTORS)
        
        if not result['servings']:
            result['servings'] = self._find_by_selectors(soup, selectors.SERVINGS_SELECTORS)
        
        if not result['image']:
            result['image'] = self._find_image(soup)
        
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
            result["ingredients"] = [self._clean_text(ingredient) for ingredient in ingredients]


        instructions = data.get("recipeInstructions", [])
        if isinstance(instructions, list):
            instructions_text = []
            for step in instructions:
                if isinstance(step, dict):
                    instructions_text.append(step.get("text"))
                elif isinstance(step, str):
                    instructions_text.append(step)
                result["instructions"] = [self._clean_text(step) for step in instructions_text]


        result["cook_time"] = data.get("cookTime")


        result['servings'] = data.get('recipeYield')


        image = data.get("image")
        if isinstance(image, dict):
            result["image"] = image.get("url")
        elif isinstance(image, list) and len(image) > 0:
            result["image"] = image[0].get("url") if isinstance(image[0], dict) else image[0]
        elif isinstance(image, str):
            result["image"] = image 

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
                    text = self._clean_text(element.get_text())
                    if text:
                        texts.append(text)
                return texts
        return []
    
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
