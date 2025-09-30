from django.db import models
from django.utils.translation import gettext_lazy as _
from app.models import TimestampedModel, StatusModel
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
    )
    meal_type = models.CharField(
        max_length=50,
        choices=MealType.choices,
        verbose_name=_("Тип блюда"),
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
    quantity = models.PositiveBigIntegerField(
        verbose_name=_("Количество"),
    )
    unit = models.CharField(
        max_length=50,
        choices=Unit.choices,
        verbose_name=_("Единица измерения"),
    )
