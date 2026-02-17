import pytest
from product.models import Product
from product.choices import Category


@pytest.fixture
def product(db, owner):
    return Product.objects.create(name="Apple", category=Category.FRUITS, created_by=owner)

@pytest.fixture
def product_1(db):
    return Product.objects.create(name="Молоко")

@pytest.fixture
def product_2(db):
    return Product.objects.create(name="Сахар")