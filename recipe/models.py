from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from app import settings
from app.models import StatusChoices, TimestampedModel, StatusModel
from recipe.choices import MealType, Unit


class Recipe(TimestampedModel, StatusModel):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Название"),
    )
    servings = models.PositiveIntegerField(
        verbose_name=_("Количество порций"),
    )
    description = models.TextField(
        verbose_name=_("Описание"),
    )
    image = models.ImageField(
        upload_to="recipes/",
        verbose_name=_("Изображение"),
        blank=True,
        null=True
    )
    meal_type = models.CharField(
        max_length=50,
        choices=MealType.choices,
        verbose_name=_("Тип блюда"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recipes"
    )

    class Meta:
        verbose_name = _("Рецепт")
        verbose_name_plural = _("Рецепты")
    
    def __str__(self):
        return self.name
    

class RecipeIngredient(TimestampedModel):
    recipe = models.ForeignKey(
        "recipe.Recipe",
        on_delete=models.CASCADE,
        related_name="ingredient",
        verbose_name=_("Рецепт"),
    )
    product = models.ForeignKey(
        "product.Product",
        on_delete=models.PROTECT,
        related_name="ingredients",
        verbose_name=_("Продукт"),
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.0'))],
        verbose_name=_("Количество"),
    )
    unit = models.CharField(
        max_length=50,
        choices=Unit.choices,
        verbose_name=_("Единица измерения"),
    )

    class Meta:
        verbose_name = _("Ингредиент")
        verbose_name_plural = _("Ингредиенты")


class RecipeSource(TimestampedModel, StatusModel):
    url = models.URLField(
        verbose_name=_("Ссылка"),
        unique=True,
    )
    title = models.CharField(
        max_length=512,
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING, 
        verbose_name=_('Статус')
    )
    metadata = models.JSONField(
        default=dict,
    )
    parsed_recipe = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        verbose_name = _("Источник рецепта")
        verbose_name_plural = _("Источники рецептов")