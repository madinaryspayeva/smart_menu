from api.v1.menu.dto.menu_dto import ShoppingItemDTO
from api.v1.menu.interfaces.menu import IShoppingCartService


class GenerateShoppingCartUseCase:
    """
    Простой usecase — делегирует работу ShoppingCartService.
    """

    def __init__(self, cart_service: IShoppingCartService):
        self.cart_service = cart_service

    def execute(self, plan_id: str) -> list[ShoppingItemDTO]:
        return self.cart_service.collect(plan_id)