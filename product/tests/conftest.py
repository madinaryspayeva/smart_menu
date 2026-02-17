import pytest
from django.contrib.auth import get_user_model
from product.models import Product
from product.choices import Category


User = get_user_model()


@pytest.fixture
def owner(db):
    return User.objects.create_user(email="owner@example.com", password="securepass")

@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(email="admin@example.com", password="adminpass")

@pytest.fixture
def other_user(db):
    return User.objects.create_user(email="other@example.com", password="securepass")

@pytest.fixture
def product(db, owner):
    return Product.objects.create(name="Apple", category=Category.FRUITS, created_by=owner)