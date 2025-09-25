from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.TextChoices):
        MEAT = "meat", _("Мясо и птица")
        FISH = "fish", _("Рыба и морепродукты")
        VEGETABLES = "vegetables", _("Овощи")
        FRUITS = "fruits", _("Фрукты и ягоды")
        DAIRY = "dairy", _("Молочные продукты и яйца")
        GROCERY = "grocery", _("Бакалея")
        OILS = "oils", _("Масла и соусы")
        BAKERY = "bakery", _("Хлебобулочные изделия")
        BEVERAGES = "beverages", _("Напитки")
        FROZEN = "frozen", _("Замороженные продукты")
        SPICES = "spices", _("Приправы и специи")
        OTHER = "other", _("Другое")