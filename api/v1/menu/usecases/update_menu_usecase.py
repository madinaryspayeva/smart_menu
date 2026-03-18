from api.v1.menu.interfaces.menu import IMenuRepository
from recipe.models import Recipe


class UpdateMenuEntryUseCase:

    def __init__(self, repository: IMenuRepository):
        self.repository = repository

    def execute(self, user_id: str, entry_id: str, recipe_id: str = None,
                servings: int = None, date=None, meal_type: str = None) -> None:
        if recipe_id:
            recipe_exists = Recipe.objects.filter(id=recipe_id, created_by_id=user_id).exists()
            if not recipe_exists:
                raise ValueError("Рецепт не найден")

        self.repository.update_entry(
            entry_id, recipe_id=recipe_id, servings=servings,
            date=date, meal_type=meal_type,
        )