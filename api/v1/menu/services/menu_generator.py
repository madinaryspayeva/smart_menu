import random

from api.v1.menu.dto.menu_dto import CreateMenuDTO, MenuEntryDTO
from api.v1.menu.interfaces.menu import IMenuGeneratorService
from recipe.models import Recipe


class MenuGeneratorService(IMenuGeneratorService):
    """
    Автоподбор рецептов для плана меню.

    Проблема: у большинства рецептов meal_type не указан или стоит
    неподходящий тип. Поэтому алгоритм работает так:

    Приоритет при выборе рецепта на конкретный приём пищи:
    1. Рецепты с ТОЧНЫМ meal_type (breakfast → breakfast)
    2. Рецепты с СОВМЕСТИМЫМ meal_type (lunch → soup, side_dish)
    3. Рецепты БЕЗ категории (пустой meal_type / некатегоризированные)
    4. Любые оставшиеся рецепты

    Антиповтор: не ставим один рецепт два дня подряд на один приём пищи.
    Глобальный антиповтор: стараемся не ставить один рецепт 
    на разные приёмы пищи в один день.
    """

    COMPATIBLE_TYPES: dict[str, list[str]] = {
        "breakfast": ["breakfast", "snack", "dessert", "drink"],
        "lunch":     ["lunch", "soup", "side_dish", "dinner"],
        "dinner":    ["dinner", "soup", "side_dish", "lunch"],
        "snack":     ["snack", "dessert", "drink", "breakfast"],
    }

    UNCATEGORIZED: set[str] = {"", None}

    def generate_entries(self, dto: CreateMenuDTO, user_id: str) -> list[MenuEntryDTO]:
        all_recipes = list(Recipe.objects.filter(created_by_id=user_id))

        if not all_recipes:
            return []
        
        categorized: dict[str, list[Recipe]] = {}
        uncategorized: list[Recipe] = []

        for recipe in all_recipes:
            mt = recipe.meal_type
            if mt in self.UNCATEGORIZED:
                uncategorized.append(recipe)
            else:
                categorized.setdefault(mt, []).append(recipe)
        
        entries: list[MenuEntryDTO] = []
        # Отслеживаем последний рецепт по meal_type (антиповтор подряд)
        last_used: dict[str, str] = {}
        # Рецепты, уже назначенные на конкретную дату (антиповтор в один день)
        used_per_date: dict[str, set[str]] = {}

        for date in sorted(dto.dates):
            date_key = date.isoformat()
            used_per_date[date_key] = set()

            for meal_type in dto.meal_types:
                recipe =self._pick(
                    categorized=categorized,
                    uncategorized=uncategorized,
                    meal_type=meal_type,
                    exclude_id=last_used.get(meal_type),
                    exclude_ids=used_per_date[date_key],
                )
                if recipe:
                    rid = str(recipe.id)
                    entries.append(MenuEntryDTO(
                        date=date,
                        meal_type=meal_type,
                        recipe_id=rid,
                        servings=dto.servings,
                    ))
                    last_used[meal_type] = rid
                    used_per_date[date_key].add(rid)

        return entries
    
    def _pick(
            self,
            categorized: dict[str, list[Recipe]],
            uncategorized: list[Recipe],
            meal_type: str,
            exclude_id: str | None,
            exclude_ids: set[str],
    ) -> Recipe | None:
        """
        Выбирает рецепт по приоритету:

        Пул 1 — точное совпадение meal_type
                 (напр. для lunch → только рецепты с meal_type="lunch")
        Пул 2 — совместимые типы
                 (напр. для lunch → soup, side_dish, dinner)
        Пул 3 — без категории
                 (meal_type пустой или None — подходят для любого приёма)
        Пул 4 — всё остальное
                 (десерт на обед лучше, чем пустая ячейка)

        Из каждого пула сначала пробуем без повторов.
        Если не получается — разрешаем повторы.
        """

        compatible = self.COMPATIBLE_TYPES.get(meal_type, [])

        # Пул 1: точное совпадение
        exact = categorized.get(meal_type, [])

        # Пул 2: совместимые (кроме точного, чтоб не дублировать)
        compat = []
        for ct in compatible:
            if ct != meal_type:
                compat.extend(categorized.get(ct, []))

        # Пул 3: без категории
        uncat = uncategorized

        # Пул 4: всё остальное
        rest = []
        skip = set(compatible) | self.UNCATEGORIZED
        for mt, recipes in categorized.items():
            if mt not in skip:
                rest.extend(recipes)

        # Пробуем пулы по приоритету
        for pool in [exact, compat, uncat, rest]:
            result = self._choose_from_pool(pool, exclude_id, exclude_ids)
            if result:
                return result

        # Совсем ничего не нашлось без повторов → разрешаем повторы
        all_recipes = exact + compat + uncat + rest
        if all_recipes:
            return random.choice(all_recipes)  # nosec B311

        return None

    def _choose_from_pool(
        self,
        pool: list[Recipe],
        exclude_id: str | None,
        exclude_ids: set[str],
    ) -> Recipe | None:
        """
        Выбирает из пула, пытаясь избежать повторов.

        1. Сначала исключаем И last_used И used_today
        2. Если пусто — исключаем только used_today
        3. Если пусто — исключаем только last_used
        4. Если пусто — возвращаем None (перейдём к след. пулу)
        """
        if not pool:
            return None

        # Строгий фильтр: не повторять подряд И не в этот день
        strict = [
            r for r in pool
            if str(r.id) != exclude_id and str(r.id) not in exclude_ids
        ]
        if strict:
            return random.choice(strict)  # nosec B311

        # Мягкий: только не в этот день
        no_today = [r for r in pool if str(r.id) not in exclude_ids]
        if no_today:
            return random.choice(no_today)  # nosec B311

        # Ещё мягче: только не подряд
        no_repeat = [r for r in pool if str(r.id) != exclude_id]
        if no_repeat:
            return random.choice(no_repeat)  # nosec B311

        return None