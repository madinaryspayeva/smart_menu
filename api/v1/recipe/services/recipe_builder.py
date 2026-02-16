import re
import sys
from api.v1.recipe.constants import AMOUNT_UNIT_RE, MEAL_TYPE_SYNONYMS, UNIT_SYNONYMS
from api.v1.recipe.dto.recipe_dto import IngredientDTO, RecipeDTO
from api.v1.recipe.interfaces.recipe_parser import IRecipeBuilderService
from api.v1.recipe.utils.helpers import UnitConverter, clean_name
from recipe.choices import Unit

RANGE_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*[-–]\s*(\d+(?:[.,]\d+)?)")

class RecipeBuilderService(IRecipeBuilderService):
    """
    Сервис для построения корректной структуры рецепта
    """
    
    def build(self, dto: RecipeDTO) -> RecipeDTO:

        normalized_ingredients = [
            self._parse_ingredient(ing) for ing in dto.ingredients
        ]

        return RecipeDTO(
            title=dto.title,
            description=dto.description,
            meal_type=self._parse_meal_type(dto),
            ingredients=normalized_ingredients,
            steps=dto.steps,
            tips=dto.tips,
            thumbnail=dto.thumbnail,
        )
    
    def _parse_meal_type(self, dto: RecipeDTO):
        context = dto.meal_type

        if not context:
            context = " ".join(filter(None, [
            dto.title,
            dto.description,
            " ".join(step.step for step in dto.steps)
        ]))

        for key, meal_type in MEAL_TYPE_SYNONYMS.items():
            pattern = r"\b{}\b".format(re.escape(key.lower()))
            if re.search(pattern, context.lower()):
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
    
    def _parse_ingredient(self, ingredient: IngredientDTO) -> IngredientDTO:
        text = ingredient.raw.lower()
    
        if not text:
            return ingredient
        
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
        
        if range_match:
            a, b = range_match.groups()
            amount = round((float(a) + float(b)) / 2, 2)
            text = text.replace(range_match.group(0), "")

        # amount + unit
        match = AMOUNT_UNIT_RE.search(text)
        
        if match:
            raw_amount = match.group("amount")
            raw_unit = match.group("unit").lower()
         
            unit = getattr(UNIT_SYNONYMS.get(raw_unit), "value", None)

            if raw_amount:
                amount = self._parse_amount(raw_amount)

            amount, unit = UnitConverter.convert(amount, unit)  #TODO fix cup problem

            text = text[:match.start()] + text[match.end():]

        name = clean_name(text)

        return IngredientDTO(
            raw=ingredient.raw,
            name=name,
            amount=amount,
            unit=unit
        )
 