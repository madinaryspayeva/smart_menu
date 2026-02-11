from django.db import models
from django.utils.translation import gettext_lazy as _


class MealType(models.TextChoices):
        BREAKFAST = "breakfast", _("Завтрак")
        LUNCH = "lunch", _("Обед")
        DINNER = "dinner", _("Ужин")
        SOUP = "soup", _("Суп")
        SNACK = "snack", _("Перекус")
        DESSERT = "dessert", _("Десерт")
        DRINK = "drink", _("Напиток")
        BABY_FOOD = "baby_food", _("Детское питание")
        SIDE_DISH = "side_dish", _("Гарнир")
        

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


class Source(models.TextChoices):
        INSTAGRAM = "instagram"
        TIKTOK = "tiktok"
        YOUTUBE = "youtube"
        WEBSITE = "website"
        UNKNOWN = "unknown"


class ContentType(models.TextChoices):
        INSTAGRAM_REEL = "instagram_reel"
        INSTAGRAM_POST = "instagram_post"
        YOUTUBE_SHORTS = "youtube_shorts"
        YOUTUBE_VIDEO = "youtube_video"
        TIKTOK_VIDEO = "tiktok_video"
        ARTICLE_OR_RECIPE = "article_or_recipe"
        UNKNOWN = "unknown"


class Domain(models.TextChoices):
        INSTAGRAM = "instagram.com"
        YOUTUBE = "youtube.com"
        TIKTOK = "tiktok.com"