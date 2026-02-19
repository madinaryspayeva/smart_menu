import pytest
from django.core.exceptions import ValidationError

from product.choices import Category
from product.models import Product


@pytest.mark.django_db
class TestProductModel:

    def test_create_product_success(self, owner):
        product = Product.objects.create(
            name="Apple",
            category=Category.FRUITS,
            created_by=owner
        )

        assert product.name == "Apple"
        assert product.category == Category.FRUITS
        assert product.created_by == owner

    def test_str_method_returns_name(self, product):
        assert str(product) == "Apple"

    def test_default_category(self, owner):
        product = Product.objects.create(
            name="Mystery Product",
            created_by=owner
        )

        assert product.category == Category.OTHER

    def test_unique_together_constraint(self, owner):
        Product.objects.create(
            name="Orange",
            created_by=owner
        )

        duplicate = Product(
            name="Orange",
            created_by=owner
        )

        with pytest.raises(ValidationError):
            duplicate.full_clean()
