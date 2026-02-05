import re
import sys
from api.v1.recipe.constants import AMOUNT_UNIT_RE, MEAL_TYPE_SYNONYMS, UNIT_SYNONYMS
from api.v1.recipe.utils.helpers import UnitConverter, clean_name
from recipe.choices import Unit

RANGE_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*[-–]\s*(\d+(?:[.,]\d+)?)")

class RecipeBuilderService:
    """
    Сервис для построения корректной структуры рецепта
    """
    
    def build_recipe(self, raw: dict) -> dict:
        meal_type = raw.get("meal_type")

        if not meal_type:
            context = " ".join(filter(None, [
            raw.get("title"),
            raw.get("description"),
            " ".join(step["step"] for step in raw.get("steps", []))
        ]))
        meal_type = self._parse_meal_type(context)

        return {
            "title": raw.get("title"),
            "description": raw.get("description"),
            "meal_type": meal_type,
            "ingredients": [self._parse_ingredient(ing) for ing in raw.get("ingredients")],
            "steps": raw.get("steps"),
            "tips": raw.get("tips"),
        }
    
    def _parse_meal_type(self, text: str | None) -> str | None:
        if not text or not isinstance(text, str):
            return None

        for key, meal_type in MEAL_TYPE_SYNONYMS.items():
            if key in text.lower():
                return meal_type.value
        
        return None
    
    def _parse_amount(self, text: str) -> float | None:
        """
        Парсит строку с числом, дробью или смешанным числом.
        Примеры:
            "150"     -> 150.0
            "1,5"     -> 1.5
            "1/2"     -> 0.5
            "1 1/2"   -> 1.5
        """
        if not text or not isinstance(text, str):
            return None

        text = text.strip()

        # --- смешанные дроби: "1 1/2" ---
        mixed_match = re.match(r"(\d+)\s+(\d+)/(\d+)", text)
        if mixed_match:
            whole, num, den = mixed_match.groups()
            return float(whole) + round(float(num) / float(den), 2)

        # --- простая дробь: "1/2" ---
        fraction_match = re.match(r"(\d+)/(\d+)", text)
        if fraction_match:
            num, den = fraction_match.groups()
            return round(float(num) / float(den), 2)

        # --- десятичное или целое число: "150", "1.5", "1,5" ---
        number_match = re.match(r"\d+(?:[.,]\d+)?", text)
        if number_match:
            return float(number_match.group(0).replace(",", "."))

        return None
    
    def _parse_ingredient(self, raw: dict) -> dict:
        text = raw.get("raw").lower()
    
        if not isinstance(text, str):
            return {
                "name": None,
                "amount": None,
                "unit": None,
            }
        
        # text  #рис(круглозернистый)-150гр.
        print(text, "!!!!!!!TEXT!!!!!!!")
        
        # Проверка "по вкусу" и подобных единиц без чисел
        for key, unit in UNIT_SYNONYMS.items():
            if unit == Unit.TO_TASTE and key in text:
                pattern = re.compile(re.escape(key), re.IGNORECASE)     
                name = pattern.sub("", text)
                return{
                    "name": clean_name(name),
                    "amount": None,
                    "unit": Unit.TO_TASTE.value, 
                }
        
        amount = None
        unit = None

        # проверка на диапозон
        range_match = RANGE_RE.search(text)
        # print(range_match, "RANGE MATCH")
        if range_match:
            a, b = range_match.groups()
            amount = round((float(a) + float(b)) / 2, 2)
            text = text.replace(range_match.group(0), "")

        # amount + unit
        match = AMOUNT_UNIT_RE.search(text)
        
        if match:
            raw_amount = match.group("amount")
            raw_unit = match.group("unit").lower()

            unit_enum = UNIT_SYNONYMS.get(raw_unit)
            raw_unit_value = unit_enum.value if unit_enum else None

            if raw_amount:
                amount = self._parse_amount(raw_amount)

            amount, unit = UnitConverter.convert(amount, raw_unit_value)

            # вырезаем amount + unit из текста
            text = text[:match.start()] + text[match.end():]

        name = clean_name(text)

        return {
            "name": name,
            "amount": amount,
            "unit": unit,
        }
 