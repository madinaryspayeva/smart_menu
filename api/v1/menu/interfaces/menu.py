from abc import ABC, abstractmethod

from api.v1.menu.dto.menu_dto import CreateMenuDTO, MenuEntryDTO, ShoppingItemDTO
from menu.models import MenuPlan


class IMenuRepository(ABC):

    @abstractmethod
    def create_menu_plan(self, user_id: str, name: str, servings: int) -> MenuPlan:
        pass
    
    @abstractmethod
    def add_entries(self, plan: MenuPlan, entries: list[MenuEntryDTO]) -> None:
        pass

    @abstractmethod
    def get_plan_with_entries(self, plan_id: str, user_id: str) -> MenuPlan | None:
        pass
    
    @abstractmethod
    def get_plan_entries_with_ingredients(self, plan_id: str) -> list:
        pass
    
    @abstractmethod
    def update_entry(self, entry_id: str, recipe_id: str = None,
                     servings: int = None, date=None, meal_type: str = None) -> None:
       pass 

    @abstractmethod
    def swap_entries(self, entry_id_1: str, entry_id_2: str) -> None:
        pass

    @abstractmethod
    def delete_entry(self, entry_id: str) -> None:
        pass

class IMenuGeneratorService(ABC):

    @abstractmethod
    def generate_entries(self, dto: CreateMenuDTO, user_id: str) -> list[MenuEntryDTO]:
        pass


class IShoppingCartService(ABC):

    @abstractmethod
    def collect(self, plan_id: str) -> list[ShoppingItemDTO]:
        pass