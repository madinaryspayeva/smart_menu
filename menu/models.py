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



