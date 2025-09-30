from django.db import models
from django.utils.translation import gettext_lazy as _


class MealType(models.TextChoices):
        BREAKFAST = "breakfast", _("Завтрак")
        LUNCH = "lunch", _("Обед")
        DINNER = "dinner", _("Ужин")
        SNACK = "snack", _("Перекус")
        DESSERT = "dessert", _("Десерт")
        DRINK = "drink", _("Напиток")
        BABY_FOOD = "baby_food", _("Детское питание")


class Unit(models.TextChoices):
        GR = "gr", _("г")
        KG = "kg", _("кг")
        ML = "ml", _("мл")
        L = "l", _("л")
        PC = "pc", _("шт")
        TSP = "tsp", _("ч.л.")
        TBSP = "tbsp", _("ст.л.")
        CUP = "cup", _("стакан")
        TO_TASTE = "to_taste", _("по вкусу")

