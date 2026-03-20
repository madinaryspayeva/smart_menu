from api.v1.common.interfaces.uow import IUnitOfWork
from api.v1.menu.dto.menu_dto import CreateMenuDTO, MenuEntryDTO
from api.v1.menu.interfaces.menu import IMenuGeneratorService, IMenuRepository
from menu.models import MenuPlan
from users.models import User


class CreateMenuUseCase:
    """
    Оркестрирует создание плана меню.

    Поток:
    1. Если entries переданы в DTO → используем их (ручной выбор)
    2. Если entries=None → генерируем автоматически через MenuGeneratorService
    3. Если генерация не дала результатов → создаём пустые слоты
    4. Создаём MenuPlan и MenuPlanEntry в одной транзакции (UoW)
    """

    def __init__(
            self,
            repository: IMenuRepository,
            generator: IMenuGeneratorService,
            uow: IUnitOfWork,
    ):
        self.repository = repository
        self.generator = generator
        self.uow = uow

    def execute(self, user: User, dto: CreateMenuDTO, empty: bool = False) -> MenuPlan:
        if empty:
            entries = self._build_empty_entries(dto)
        elif dto.entries:
            entries = dto.entries
        else:
            entries = self.generator.generate_entries(dto, str(user.id))
            if not entries:
                entries = self._build_empty_entries(dto)

        with self.uow:
            plan = self.repository.create_menu_plan(
                user_id=str(user.id),
                name=dto.name,
                servings=dto.servings,
            )
            self.repository.add_entries(plan, entries)

        return plan

    def _build_empty_entries(self, dto: CreateMenuDTO) -> list[MenuEntryDTO]:
        return [
            MenuEntryDTO(
                date=d,
                meal_type=mt,
                recipe_id=None,
                servings=dto.servings,
            )
            for d in dto.dates
            for mt in dto.meal_types
        ]