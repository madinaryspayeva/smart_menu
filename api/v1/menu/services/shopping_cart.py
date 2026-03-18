from collections import defaultdict
from decimal import Decimal

from api.v1.menu.dto.menu_dto import ShoppingItemDTO
from api.v1.menu.interfaces.menu import IMenuRepository, IShoppingCartService
from recipe.choices import Unit


class ShoppingCartService(IShoppingCartService):
    """
    Собирает список покупок из плана меню.

    Главная задача — правильно пересчитать количество ингредиентов:
    1. Каждый entry имеет свои servings (порции)
    2. Рецепт имеет свои servings (на сколько порций рассчитан)
    3. Формула: нужно = (quantity / recipe.servings) * entry.servings
    
    Пример:
    Рецепт «Борщ» на 4 порции, мясо 800гр.
    Entry на понедельник: 2 порции → 800 / 4 * 2 = 400гр
    Entry на среду: 2 порции → 400гр
    Итого в корзине: мясо 800гр (а не 1600гр!)
    
    Подождите — нет, тут 400 + 400 = 800гр, потому что это ДВА дня.
    Именно так и должно работать: мы готовим ДВАЖДЫ.
    
    НО если пользователь хочет приготовить 1 раз на 2 дня —
    он ставит 1 entry с servings=4, а не 2 entry по 2.
    """

     # Конвертация в базовые единицы для суммирования
    TO_BASE = {
        Unit.KG: (Unit.GR, Decimal("1000")),    # 1 кг = 1000 гр
        Unit.L: (Unit.ML, Decimal("1000")),      # 1 л = 1000 мл
    }
    # Обратная конвертация для красивого отображения
    FROM_BASE = {
        Unit.GR: (Unit.KG, Decimal("1000")),     # ≥1000 гр → кг
        Unit.ML: (Unit.L, Decimal("1000")),      # ≥1000 мл → л
    }

    def __init__(self, repository: IMenuRepository):
        self.repository = repository
    
    def collect(self, plan_id: str) -> list[ShoppingItemDTO]:
        entries = self.repository.get_plan_entries_with_ingredients(plan_id)

        # Аккумулятор: {(product_id, base_unit): {"quantity": Decimal, ...}}
        cart: dict[tuple, dict] = {}

        for entry in entries:
            recipe = entry.recipe
            if not recipe:
                continue
            recipe_servings = recipe.servings

            for ing in recipe.ingredient.all():
                if not ing.product.name:
                    continue
                quantity = ing.quantity or Decimal("0") #TODO change to None
                try:
                    unit = Unit(ing.unit)
                except (ValueError, KeyError):
                    unit = Unit.TO_TASTE

                # Пересчёт порций
                # (кол-во в рецепте / порции рецепта) * порции этой записи
                scaled_qty = (quantity / Decimal(str(recipe_servings))) * Decimal(str(entry.servings))

                # Конвертация в базовую единицу
                if unit in self.TO_BASE:
                    base_unit, factor = self.TO_BASE[unit]
                    scaled_qty *= factor
                    unit = base_unit

                # Ключ: (product_id, unit) — один продукт может быть в гр и в шт
                key = (str(ing.product_id), unit)

                if key in cart:
                    cart[key]["quantity"] += scaled_qty
                else:
                    cart[key] = {
                        "product": ing.product,
                        "quantity": scaled_qty,
                        "unit": unit,
                    }
        
        return self._format(cart)
    
    def _format(self, cart: dict) -> list[ShoppingItemDTO]:
        """
        Конвертирует обратно в удобные единицы и возвращает список DTO.
        1000гр → 1кг, 1500мл → 1.5л
        """
        result = []
        for item in cart.values():
            quantity = item["quantity"]
            unit = item["unit"]
            product = item["product"]

            # Обратная конвертация
            if unit in self.FROM_BASE:
                big_unit, threshold = self.FROM_BASE[unit]
                if quantity >= threshold:
                    quantity = quantity / threshold
                    unit = big_unit

            result.append(ShoppingItemDTO(
                product_name=product.name,
                product_id=str(product.id),
                category=product.category,
                quantity=float(quantity.quantize(Decimal("0.01"))),
                unit=unit.label,
            ))
        # Сортировка: по категории → по названию
        result.sort(key=lambda x: (x.category, x.product_name))
        return result