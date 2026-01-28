import re
from api.v1.recipe.constants import AMOUNT_RE, LLM_SCHEMA, MEAL_TYPE_SYNONYMS, UNIT_SYNONYMS
from api.v1.recipe.utils.helpers import UnitConverter, clean_name
from recipe.choices import Unit



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

    def _parse_unit(self, text: str) -> str | None:
        if not isinstance(text, str):
            return None
        
        for key, unit in UNIT_SYNONYMS.items():
            if key in text.lower():
                return unit.value
        
        return None
    
    def _parse_meal_type(self, text: str | None) -> str | None:
        if not text or not isinstance(text, str):
            return None

        for key, meal_type in MEAL_TYPE_SYNONYMS.items():
            if key in text.lower():
                return meal_type.value
        
        return None
    
    def _parse_amount(self, text: str) -> float | None:
        match = AMOUNT_RE.search(text)
        if not match:
            return None
        
        value = match.group(1)
        if "/" in value:
            num, den = value.split("/")
            return round(float(num) / float(den), 2)
        
        return float(value.replace(",", "."))
    
    def _parse_ingredient(self, raw: dict) -> dict:
        text = raw.get("raw")
        if not isinstance(text, str):
            return {
                "name": None,
                "amount": None,
                "unit": None,
            }
        
        raw_unit = self._parse_unit(text)
        amount = None if raw_unit == Unit.TO_TASTE.value else self._parse_amount(text)

        amount, unit = UnitConverter.convert(amount, raw_unit)

        name = text

        if amount:
            name = AMOUNT_RE.sub("", name)
        
        if unit and unit != Unit.TO_TASTE.value:
            for key, u in UNIT_SYNONYMS.items():
                if u == unit:
                    pattern = rf"\b{re.escape(key)}\b"
                    name = re.sub(pattern, "", name, flags=re.IGNORECASE)
        
        name = clean_name(name)

        return {
        "name": name.strip(),
        "amount": amount,
        "unit": unit
    }
        
    