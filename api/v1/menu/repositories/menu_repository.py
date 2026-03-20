from django.db import transaction

from api.v1.menu.dto.menu_dto import MenuEntryDTO
from api.v1.menu.interfaces.menu import IMenuRepository
from menu.models import MenuPlan, MenuPlanEntry


class MenuRepository(IMenuRepository):
    def create_menu_plan(self, user_id: str, name: str, servings: int) -> MenuPlan:
        return MenuPlan.objects.create(
            created_by_id=user_id, 
            name=name,
            servings=servings,
        )
    
    def add_entries(self, plan: MenuPlan, entries: list[MenuEntryDTO]) -> None:
        objects = [
            MenuPlanEntry(
                menu_plan=plan,
                date=entry.date,
                meal_type=entry.meal_type,
                recipe_id=entry.recipe_id,
                servings=entry.servings,
            )
            for entry in entries
        ]
        MenuPlanEntry.objects.bulk_create(objects)
    
    def get_plan_with_entries(self, plan_id: str, user_id: str) -> MenuPlan | None:
        return (
            MenuPlan.objects
            .filter(id=plan_id, created_by_id=user_id)
            .prefetch_related("entries__recipe")
            .first()
        )
    
    def get_plan_entries_with_ingredients(self, plan_id: str) -> list:
        return (
            MenuPlanEntry.objects
            .filter(menu_plan_id=plan_id)
            .select_related("recipe")
            .prefetch_related("recipe__ingredient__product")
        )

    def update_entry(self, entry_id: str, recipe_id: str = None,
                     servings: int = None, date=None, meal_type: str = None) -> None:
        updates = {}
        if recipe_id is not None:
            updates["recipe_id"] = recipe_id
        if servings is not None:
            updates["servings"] = servings
        if date is not None:
            updates["date"] = date
        if meal_type is not None:
            updates["meal_type"] = meal_type
        if updates:
            MenuPlanEntry.objects.filter(id=entry_id).update(**updates)
    
    def swap_entries(self, entry_id_1: str, entry_id_2: str) -> None:
        """Атомарно меняет рецепты и порции между двумя записями."""
        with transaction.atomic():
            e1 = MenuPlanEntry.objects.select_for_update().get(id=entry_id_1)
            e2 = MenuPlanEntry.objects.select_for_update().get(id=entry_id_2)
            e1.recipe_id, e2.recipe_id = e2.recipe_id, e1.recipe_id
            e1.servings, e2.servings = e2.servings, e1.servings
            e1.save(update_fields=["recipe_id", "servings"])
            e2.save(update_fields=["recipe_id", "servings"])

    def create_entry(self, plan_id: str, date, meal_type: str,
                     recipe_id: str, servings: int) -> MenuPlanEntry:
        return MenuPlanEntry.objects.create(
            menu_plan_id=plan_id,
            date=date,
            meal_type=meal_type,
            recipe_id=recipe_id,
            servings=servings,
        )

    def clear_entry_recipe(self, entry_id: str, user_id: str) -> bool:
        updated = MenuPlanEntry.objects.filter(
            id=entry_id,
            menu_plan__created_by_id=user_id,
        ).update(recipe_id=None)
        return updated > 0

    def delete_entry(self, entry_id: str) -> None:
        MenuPlanEntry.objects.filter(id=entry_id).delete()
        