import re

from api.v1.recipe.constants import (
    AMOUNT_PREFIX_RE,
    AMOUNT_SUFFIX_RE,
    AMOUNT_UNIT_RE,
    INGREDIENT_NOISE_WORDS,
    MEAL_TYPE_SYNONYMS,
    RANGE_RE,
    UNIT_ONLY_RE,
    UNIT_SYNONYMS,
)
from api.v1.recipe.dto.recipe_dto import IngredientDTO, RecipeDTO
from api.v1.recipe.interfaces.recipe_parser import IRecipeBuilderService
from api.v1.recipe.utils.helpers import UnitConverter, clean_name
from recipe.choices import Unit


class RecipeBuilderService(IRecipeBuilderService):
    """
    Сервис для построения корректной структуры рецепта.
    """

    def build(self, dto: RecipeDTO) -> RecipeDTO:
        normalized_ingredients = [
            self._parse_ingredient(ing)
            for ing in dto.ingredients
            if not self._is_noise(ing.raw)
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

    # ------------------------------------------------------------------
    # Фильтрация мусорных строк
    # ------------------------------------------------------------------

    def _is_noise(self, raw: str | None) -> bool:
        if not raw:
            return True
        return raw.strip().lower() in INGREDIENT_NOISE_WORDS

    # ------------------------------------------------------------------
    # Meal type
    # ------------------------------------------------------------------

    def _parse_meal_type(self, dto: RecipeDTO):
        context = dto.meal_type

        if not context:
            context = " ".join(filter(None, [
                dto.title,
                dto.description,
                " ".join(step.step for step in dto.steps),
            ]))

        for key, meal_type in MEAL_TYPE_SYNONYMS.items():
            pattern = rf"\b{re.escape(key.lower())}\b"
            if re.search(pattern, context.lower()):
                return meal_type.value

        return None

    # ------------------------------------------------------------------
    # Amount parsing
    # ------------------------------------------------------------------

    def _parse_amount(self, text: str) -> float | None:
        """
        Парсит строку с числом, дробью или смешанным числом.
            "150"     -> 150.0
            "1,5"     -> 1.5
            "0,5"     -> 0.5
            "1/2"     -> 0.5
            "1/4"     -> 0.25
            "1 1/2"   -> 1.5
        """
        if not text or not isinstance(text, str):
            return None

        text = text.strip()

        mixed_match = re.match(r"(\d+)\s+(\d+)/(\d+)", text)
        if mixed_match:
            whole, num, den = mixed_match.groups()
            return float(whole) + round(float(num) / float(den), 2)

        fraction_match = re.match(r"(\d+)/(\d+)", text)
        if fraction_match:
            num, den = fraction_match.groups()
            return round(float(num) / float(den), 2)

        number_match = re.match(r"\d+(?:[.,]\d+)?", text)
        if number_match:
            return float(number_match.group(0).replace(",", "."))

        return None

    # ------------------------------------------------------------------
    # Ingredient parsing
    # ------------------------------------------------------------------

    def _parse_ingredient(self, ingredient: IngredientDTO) -> IngredientDTO:
        text = ingredient.raw.strip()

        if not text:
            return ingredient

        lower = text.lower()

        # --- "по вкусу" / "щепотка" и аналоги ---
        for key, unit in UNIT_SYNONYMS.items():
            if unit == Unit.TO_TASTE and key in lower:
                pattern = re.compile(re.escape(key), re.IGNORECASE)
                name = pattern.sub("", text)
                return IngredientDTO(
                    raw=ingredient.raw,
                    name=clean_name(name),
                    amount=None,
                    unit=Unit.TO_TASTE.value,
                )

        amount: float | None = None
        unit: str | None = None
        working = lower

        # --- диапазон: "40–50 г" или "1–2 ст. л." ---
        # После вырезания числового диапазона единица остаётся в строке —
        # ищем её отдельным паттерном UNIT_ONLY_RE
        range_match = RANGE_RE.search(working)
        if range_match:
            a, b = range_match.groups()
            amount = round(
                (float(a.replace(",", ".")) + float(b.replace(",", "."))) / 2, 2
            )
            working = working[: range_match.start()] + " " + working[range_match.end():]

            # ищем единицу в оставшемся тексте
            unit_only_match = UNIT_ONLY_RE.search(working)
            if unit_only_match:
                raw_unit = unit_only_match.group("unit").lower()
                unit_enum = UNIT_SYNONYMS.get(raw_unit)
                unit = unit_enum.value if unit_enum else None
                amount, unit = UnitConverter.convert(amount, unit)
                # вырезаем найденную единицу из строки
                working = working[: unit_only_match.start()] + " " + working[unit_only_match.end():]

        # --- число + единица (в любом месте строки) ---
        if unit is None:
            unit_match = AMOUNT_UNIT_RE.search(working)
            if unit_match:
                if amount is None:
                    amount = self._parse_amount(unit_match.group("amount"))

                raw_unit = unit_match.group("unit").lower()
                unit_enum = UNIT_SYNONYMS.get(raw_unit)
                unit = unit_enum.value if unit_enum else None

                amount, unit = UnitConverter.convert(amount, unit)
                working = working[: unit_match.start()] + " " + working[unit_match.end():]

            else:
                # --- "1банан" — число слитно с названием ---
                prefix_match = AMOUNT_PREFIX_RE.match(working.strip())
                if prefix_match:
                    if amount is None:
                        amount = self._parse_amount(prefix_match.group(1))
                    working = prefix_match.group(2)
                    unit = Unit.PC.value

                else:
                    # --- "молоко 200" — число в конце без единицы ---
                    suffix_match = AMOUNT_SUFFIX_RE.search(working)
                    if suffix_match:
                        if amount is None:
                            amount = self._parse_amount(suffix_match.group(1))
                        working = working[: suffix_match.start()]
                        unit = Unit.PC.value

        # если amount нашли, но unit так и не определился → штуки
        if amount is not None and unit is None:
            unit = Unit.PC.value

        name = clean_name(working)

        return IngredientDTO(
            raw=ingredient.raw,
            name=name,
            amount=amount,
            unit=unit,
        )