import re

from api.v1.recipe.constants import CONVERSION, UNIT_SYNONYMS 


def clean_name(name: str) -> str:
    name = re.sub(r"[^а-яА-Яa-zA-Z0-9\s]", " ", name)
    return re.sub(r"\s+", " ", name).strip()

class UnitConverter:
    """
    Конвертирует amount + unit в канонический Unit
    """
    
    @classmethod
    def convert(cls, amount: float | None, raw_unit: str | None):
        if amount is None or not raw_unit:
            return amount, raw_unit

        key = raw_unit.lower() #oz

        if key not in CONVERSION:
            return amount, UNIT_SYNONYMS.get(key)
        
        factor = CONVERSION[key]
        target_unit = UNIT_SYNONYMS.get(key)

        return round(amount * factor, 2), target_unit