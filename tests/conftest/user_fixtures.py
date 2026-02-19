import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def owner(db):
    """Обычный пользователь"""
    return User.objects.create_user(email="owner@example.com", password="securepass")

@pytest.fixture
def superuser(db):
    """Суперпользователь"""
    return User.objects.create_superuser(email="admin@example.com", password="adminpass")

@pytest.fixture
def other_user(db):
    """Другой обычный пользователь"""
    return User.objects.create_user(email="other@example.com", password="securepass")

@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@example.com", password="securepass")

@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client