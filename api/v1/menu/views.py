from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.common.uow.django_uow import DjangoUnitOfWork
from api.v1.menu.dto.menu_dto import CreateMenuDTO, MenuEntryDTO
from api.v1.menu.repositories.menu_repository import MenuRepository
from api.v1.menu.serializers import AddMenuEntrySerializer, CreateMenuSerializer, ShoppingCartSerializer, SwapEntriesSerializer, UpdateMenuEntrySerializer
from api.v1.menu.services.menu_generator import MenuGeneratorService
from api.v1.menu.services.shopping_cart import ShoppingCartService
from api.v1.menu.usecases.create_menu_usecase import CreateMenuUseCase
from api.v1.menu.usecases.generate_shopping_cart_usecase import GenerateShoppingCartUseCase
from api.v1.menu.usecases.update_menu_usecase import UpdateMenuEntryUseCase


class CreateMenuAPIView(APIView):
    """
    POST /api/v1/menu/create/
    
    Принимает:
    {
        "name": "Меню на неделю",
        "servings": 2,
        "dates": ["2026-03-16", "2026-03-17", "2026-03-18"],
        "meal_types": ["breakfast", "lunch", "dinner"],
        "entries": null   ← null = автоподбор, или список ручных записей
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateMenuSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        dto = CreateMenuDTO(
            name=data["name"],
            servings=data["servings"],
            dates=data["dates"],
            meal_types=data["meal_types"],
            entries=self._parse_entries(data.get("entries")) if data.get("entries") else None,
        )

        use_case = CreateMenuUseCase(
            repository=MenuRepository(),
            generator=MenuGeneratorService(),
            uow=DjangoUnitOfWork(),
        )

        try:
            plan = use_case.execute(request.user, dto)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"id": str(plan.id), "name": plan.name},
            status=status.HTTP_201_CREATED,
        )

    def _parse_entries(self, raw_entries: list[dict]) -> list[MenuEntryDTO]:
        return [
            MenuEntryDTO(
                date=e["date"],
                meal_type=e["meal_type"],
                recipe_id=e["recipe_id"],
                servings=e["servings"],
            )
            for e in raw_entries
        ]


class UpdateMenuEntryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, entry_id):
        serializer = UpdateMenuEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        use_case = UpdateMenuEntryUseCase(repository=MenuRepository())

        try:
            use_case.execute(
                user_id=str(request.user.id),
                entry_id=entry_id,
                recipe_id=str(data["recipe_id"]) if data.get("recipe_id") else None,
                servings=data.get("servings"),
                date=data.get("date"),
                meal_type=data.get("meal_type"),
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"ok": True}, status=status.HTTP_200_OK)


class AddMenuEntryAPIView(APIView):
    """POST /api/v1/menu/entry/add/ — создаёт новую запись в плане."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddMenuEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        repository = MenuRepository()

        # Проверяем, что план принадлежит пользователю
        plan = repository.get_plan_with_entries(
            str(data["plan_id"]), str(request.user.id)
        )
        if not plan:
            return Response(
                {"error": "План не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )

        entry = repository.create_entry(
            plan_id=str(data["plan_id"]),
            date=data["date"],
            meal_type=data["meal_type"],
            recipe_id=str(data["recipe_id"]),
            servings=data["servings"],
        )

        return Response(
            {"entry_id": str(entry.id)},
            status=status.HTTP_201_CREATED,
        )


class SwapEntriesAPIView(APIView):
    """POST /api/v1/menu/swap/ — атомарный своп рецептов между двумя записями."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SwapEntriesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        repository = MenuRepository()
        try:
            repository.swap_entries(
                str(data["entry_id_1"]),
                str(data["entry_id_2"]),
            )
        except Exception:
            return Response({"error": "Ошибка при перестановке"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"ok": True}, status=status.HTTP_200_OK)


class ShoppingCartAPIView(APIView):
    """
    GET /api/v1/menu/<uuid:plan_id>/cart/
    
    Возвращает список покупок для плана меню.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, plan_id):
        repository = MenuRepository()

        # Проверяем, что план принадлежит пользователю
        plan = repository.get_plan_with_entries(str(plan_id), str(request.user.id))
        if not plan:
            return Response(
                {"error": "План не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart_service = ShoppingCartService(repository=repository)
        use_case = GenerateShoppingCartUseCase(cart_service)
        items = use_case.execute(str(plan_id))

        serializer = ShoppingCartSerializer(items, many=True)
        return Response(serializer.data)
