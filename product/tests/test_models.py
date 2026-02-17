from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from product.choices import Category
from product.models import Product


User = get_user_model()


class ProductModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="securepass"
        )
    
    def test_create_product_success(self):
        product = Product.objects.create(
            name="Apple",
            category=Category.FRUITS,
            created_by=self.user
        )
        self.assertEqual(product.name, "Apple")
        self.assertEqual(product.category, Category.FRUITS)
        self.assertEqual(product.created_by, self.user)

    def test_str_method_returns_name(self):
        product = Product.objects.create(
            name="Banana",
            category=Category.FRUITS,
            created_by=self.user
        )
        self.assertEqual(str(product), "Banana")
    
    def test_default_category(self):
        product = Product.objects.create(
            name="Mystery Product",
            created_by=self.user
        )
        self.assertEqual(product.category, Category.OTHER)
    
    def test_unique_together_constraint(self):
        Product.objects.create(
            name="Orange",
            created_by=self.user
        )
        duplicate = Product(
            name="Orange",
            created_by=self.user
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean() 
