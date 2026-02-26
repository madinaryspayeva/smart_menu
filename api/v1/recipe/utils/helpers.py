import re

from api.v1.recipe.constants import CONVERSION, UNIT_SYNONYMS


def clean_name(name: str) -> str:
    # убираем содержимое скобок вместе со скобками: (≈300 г), (по желанию), (у меня черничный)
    name = re.sub(r"\(.*?\)", " ", name)
    # убираем смешанные дроби "1 1/2"
    name = re.sub(r"\d+\s+\d+/\d+", "", name)
    # убираем простые дроби "1/2"
    name = re.sub(r"\d+/\d+", "", name)
    # убираем одиночные числа (целые и десятичные)
    name = re.sub(r"\b\d+(?:[.,]\d+)?\b", "", name)
    # убираем всё кроме букв (рус/англ), пробелов и дефиса
    name = re.sub(r"[^а-яёА-ЯЁa-zA-Z\s\-]", " ", name)
    # убираем одиночный дефис не окружённый буквами
    name = re.sub(r"(?<!\w)-(?!\w)", " ", name)
    # схлопываем пробелы
    return re.sub(r"\s+", " ", name).strip().lower()


class UnitConverter:
    """
    Конвертирует amount + unit в канонический Unit.
    Например: oz → граммы, lb → граммы.
    """

    @classmethod
    def convert(cls, amount: float | None, raw_unit: str | None):
        if amount is None or not raw_unit:
            return amount, raw_unit

        key = raw_unit.lower()

        if key not in CONVERSION:
            return amount, raw_unit

        factor = CONVERSION[key]
        target_unit = UNIT_SYNONYMS.get(key)
        converted_unit = target_unit.value if target_unit else raw_unit

        return round(amount * factor, 2), converted_unit