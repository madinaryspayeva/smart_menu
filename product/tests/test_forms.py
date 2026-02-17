import pytest
from django.test import RequestFactory
from product.forms import ProductForm
from product.models import Product
from product.choices import Category


@pytest.mark.django_db
class TestProductForm:

    def test_form_valid_data(self, owner):
        factory = RequestFactory()
        request = factory.get("/")
        request.user = owner

        form = ProductForm(
            data={
                "name": "Apple",
                "category": Category.FRUITS,
            },
            request=request,
        )

        assert form.is_valid()

        product = form.save(commit=False)
        product.created_by = owner
        product.save()

        assert product.name == "Apple"
        assert product.category == Category.FRUITS
        assert product.created_by == owner

    def test_form_duplicate_name_for_user(self, owner):
        factory = RequestFactory()
        request = factory.get("/")
        request.user = owner

        Product.objects.create(name="Apple", created_by=owner)

        form = ProductForm(
            data={
                "name": "Apple",
                "category": Category.FRUITS,
            },
            request=request,
        )

        assert not form.is_valid()
        assert "name" in form.errors
        assert form.errors["name"][0] == "Продукт с таким названием уже существует."

    def test_form_allows_same_name_for_different_users(self, owner, other_user):
        factory = RequestFactory()
        request = factory.get("/")
        request.user = owner

        Product.objects.create(name="Apple", created_by=other_user)

        form = ProductForm(
            data={
                "name": "Apple",
                "category": Category.FRUITS,
            },
            request=request,
        )

        assert form.is_valid()
