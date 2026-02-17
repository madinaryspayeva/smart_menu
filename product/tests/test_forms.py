from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django import forms
from product.forms import ProductForm
from product.models import Product
from product.choices import Category


User = get_user_model()


class ProductFormTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="securepass"
        )
        self.request = self.factory.get("/")
        self.request.user = self.user
    
    def test_form_valid_data(self):
        form = ProductForm(
            data={
                "name": "Apple",
                "category": Category.FRUITS
            },
            request=self.request
        )
        self.assertTrue(form.is_valid())
        product = form.save(commit=False)
        product.created_by = self.user
        product.save()

        self.assertEqual(product.name, "Apple")
        self.assertEqual(product.category, Category.FRUITS)
        self.assertEqual(product.created_by, self.user)
    
    def test_form_duplicate_name_for_user(self):
        Product.objects.create(name="Apple", created_by=self.user)

        form = ProductForm(
            data={
                "name": "Apple",
                "category": Category.FRUITS
            },
            request=self.request
        )
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertEqual(
            form.errors["name"][0],
            "Продукт с таким названием уже существует."
        )
    
    def test_form_allows_same_name_for_different_users(self):
        other_user = User.objects.create_user(email="otheruser@example.com", password="securepass")
        Product.objects.create(name="Apple", created_by=other_user)

        form = ProductForm(
            data={
                "name": "Apple",
                "category": Category.FRUITS
            },
            request=self.request
        )
        self.assertTrue(form.is_valid())
    
