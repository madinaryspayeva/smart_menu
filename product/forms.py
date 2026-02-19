from django import forms
from django.utils.translation import gettext_lazy as _

from product.models import Product


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Product
        fields = ["name", "category"]

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")

        if name and self.request:
            if Product.objects.filter(
                name=name, 
                created_by=self.request.user
            ).exclude(pk=self.instance.pk).exists():
                self.add_error('name', _("Продукт с таким названием уже существует."))

        return cleaned_data