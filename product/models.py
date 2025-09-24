from django.db import models
from django.utils.translation import gettext_lazy as _

from app import settings
from app.models import TimestampedModel
from product.choices import Category


class Product(TimestampedModel):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Название")
    )
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.OTHER,
        verbose_name=_("Категория")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products"
    )

    class Meta:
        unique_together = ("name", "created_by")
        verbose_name = _("Продукт")
        verbose_name_plural = _("Продукты")
    
    def __str__(self):
        return self.name