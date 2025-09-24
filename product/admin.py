from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from product.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "created_by", ]
    search_fields = ("name",)