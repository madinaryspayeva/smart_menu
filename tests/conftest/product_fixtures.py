import pytest

from product.choices import Category
from product.models import Product


@pytest.fixture
def product(db, owner):
    return Product.objects.create(name="Apple", category=Category.FRUITS, created_by=owner)

@pytest.fixture
def product_1(db):
    return Product.objects.create(name="Молоко")

@pytest.fixture
def product_2(db):
    return Product.objects.create(name="Сахар")

@pytest.fixture
def products(owner):
    return [
            Product.objects.create(name="Apple", category=Category.FRUITS, created_by=owner),
            Product.objects.create(name="Banana", category=Category.FRUITS, created_by=owner),
            Product.objects.create(name="Carrot", category=Category.VEGETABLES, created_by=owner),
        ]