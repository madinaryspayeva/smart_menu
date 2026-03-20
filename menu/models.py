from django.db import models
from django.utils.translation import gettext_lazy as _

from app import settings
from app.models import TimestampedModel
from recipe.choices import MealType
from recipe.models import Recipe


class MenuPlan(TimestampedModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="menu_plans",
        verbose_name=_("Пользователь")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Название")
    )
    servings = models.PositiveIntegerField(
        default=2,
        verbose_name=_("Количество порций")
    )

    @property
    def date_range(self):
        date_min = getattr(self, "date_min", None)
        date_max = getattr(self, "date_max", None)
        if not date_min:
            return "Нет дат"
        if date_min == date_max:
            return date_min.strftime("%d.%m.%Y")
        return f"{date_min.strftime('%d')}–{date_max.strftime('%d %b')}"
    
    @property
    def preview_images(self):
        entries = (
            self.entries
            .filter(recipe__isnull=False, recipe__image__isnull=False)
            .exclude(recipe__image="")
            .select_related("recipe")
        )
        seen = set()
        images = []
        for entry in entries:
            name = entry.recipe.image.name
            if name and name not in seen:
                seen.add(name)
                images.append(entry.recipe.image.url)
            if len(images) >= 4:
                break
        return images

    @property
    def empty_slots(self):
        """Кол-во пустых слотов для выравнивания превью до 4."""
        count = len(self.preview_images)
        return range(4 - count) if count < 4 else range(0)    

    class Meta:
        verbose_name = _("План меню")
        verbose_name_plural = _("Планы меню")
        ordering = ["-created"]

    def __str__(self) -> str:
        return self.name


class MenuPlanEntry(TimestampedModel):
    menu_plan = models.ForeignKey(
        MenuPlan,
        on_delete=models.CASCADE,
        related_name="entries",
        verbose_name=_("План меню")
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="menu_entries",
        verbose_name=_("Рецепт"),
        null=True,
        blank=True,
    )
    meal_type = models.CharField(
        max_length=20,
        choices=MealType.choices,
        verbose_name=_("Прием пищи")
    )
    date = models.DateField(
        verbose_name=_("Дата")
    )
    servings = models.PositiveIntegerField(
        verbose_name=_("Количество порций")
    )

    class Meta:
        verbose_name = _("Запись в меню")
        verbose_name_plural = _("Записи в меню")
        ordering = ["date", "meal_type"]

    def __str__(self) -> str:
        return f"{self.date} - {self.meal_type}: {self.recipe.name}"



