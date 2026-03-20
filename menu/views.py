from collections import defaultdict
from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Min, Max, Q
from django.shortcuts import redirect
from django.views.generic import DetailView, TemplateView, ListView

from api.v1.common.uow.django_uow import DjangoUnitOfWork
from api.v1.menu.dto.menu_dto import CreateMenuDTO
from api.v1.menu.repositories.menu_repository import MenuRepository
from api.v1.menu.services.menu_generator import MenuGeneratorService
from api.v1.menu.services.shopping_cart import ShoppingCartService
from api.v1.menu.usecases.create_menu_usecase import CreateMenuUseCase
from api.v1.menu.usecases.generate_shopping_cart_usecase import GenerateShoppingCartUseCase
from app.views import AuthRequiredView
from menu.models import MenuPlan


class MenuPlanCreateView(LoginRequiredMixin, TemplateView):
    """
    Страница с календарём для создания меню.
    
    GET: показывает календарь + форму (порции, название, приёмы пищи).
    POST: принимает выбранные даты из JS-календаря, генерирует меню.
    
    Календарь реализуется на фронте через JS:
    - Показывает текущий месяц
    - Пользователь кликает по дням (toggle выбора)
    - Быстрые кнопки: "Вся неделя", "Пн-Пт", "Весь месяц"
    - Выбранные даты отправляются как hidden inputs или JSON
    """
    template_name = "menu/create.html"

    def post(self, request):
        # Даты приходят как список строк из JS-календаря
        dates_raw = request.POST.getlist("dates")
        dates = [date.fromisoformat(d) for d in dates_raw if d]

        meal_types = request.POST.getlist("meal_types")
        name = request.POST.get("name", "")
        servings = int(request.POST.get("servings", 2)) #TODO add servings input checking
                                                        #magic 2 is not ok
        if not dates or not meal_types:
            return self.render_to_response(self.get_context_data(
                error="Выберите хотя бы одну дату и один приём пищи"
            ))  
        
        dto = CreateMenuDTO(
            name=name or f"Меню на {len(dates)} дней",
            servings=servings,
            dates=dates,
            meal_types=meal_types,      
        )

        use_case = CreateMenuUseCase(
            repository=MenuRepository(),
            generator=MenuGeneratorService(),
            uow=DjangoUnitOfWork(),
        )

        is_empty = request.POST.get("empty") == "1"
        plan = use_case.execute(request.user, dto, empty=is_empty)
        return redirect("menu:detail", pk=plan.id)


class MenuPlanListView(AuthRequiredView, ListView):
    model = MenuPlan
    template_name = "menu/list.html"
    context_object_name = "plans"
    paginate_by = 4

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(created_by=self.request.user)
            .annotate(
                total_recipes=Count("entries", filter=Q(entries__recipe__isnull=False)),
                total_days=Count("entries__date", distinct=True),
                date_min=Min("entries__date"),
                date_max=Max("entries__date"),
            ).order_by("-created")
        )   


class MenuPlanDetailView(LoginRequiredMixin, DetailView):
    """
    Детальная страница плана — таблица дат × приёмов пищи.
    Кнопка «Собрать корзину» ведёт на cart.
    """
    model = MenuPlan
    template_name = "menu/detail.html"
    context_object_name = "plan"

    def get_queryset(self):
        return MenuPlan.objects.filter(created_by=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entries = self.object.entries.select_related("recipe").order_by("date", "meal_type")

        # Структура для шаблона: {date: {meal_type: [entry, ...]}}
        schedule = defaultdict(lambda: defaultdict(list))
        meal_types_used = set()
        for entry in entries:
            schedule[entry.date][entry.meal_type].append(entry)
            meal_types_used.add(entry.meal_type)

        context["schedule"] = {d: dict(mt) for d, mt in schedule.items()}
        context["sorted_dates"] = sorted(schedule.keys())
        context["meal_types"] = sorted(meal_types_used)
        return context
    

class MenuPlanShoppingCartView(LoginRequiredMixin, DetailView):
    """
    Корзина закупок — сгруппированный список продуктов.
    """
    model = MenuPlan
    template_name = "menu/shopping_cart.html"
    context_object_name = "plan"

    def get_queryset(self):
        return MenuPlan.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        repository = MenuRepository()
        cart_service = ShoppingCartService(repository=repository)
        use_case = GenerateShoppingCartUseCase(cart_service)
        items = use_case.execute(str(self.object.pk))

        # Группируем по категориям
        categories = defaultdict(list)
        for item in items:
            categories[item.category].append(item)

        context["categories"] = dict(categories)
        context["total_items"] = len(items)
        return context