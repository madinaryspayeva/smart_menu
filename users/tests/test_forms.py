from django.test import TestCase, Client
from users.forms import CustomSignupForm
from users.models import User


class CustomSignupFormTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_first_name_field_required(self):
        """Поле first_name должно быть обязательным"""

        form_data = {
            "email": "test@example.com",
            "password1": "securepass",
            "password2": "securepass",
        }
        form = CustomSignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
    
    def test_form_valid_with_all_fields(self):
         """Форма валидна при корректных данных"""

         form_data = {
            "email": "test@example.com",
            "password1": "securepass",
            "password2": "securepass",
            "first_name": "Test"
         }
         form = CustomSignupForm(data=form_data)
         self.assertTrue(form.is_valid())
    
    def test_save_creates_user_with_first_name(self):
        """Метод save создает пользователя с указанным first_name"""

        form_data = {
            "email": "test@example.com",
            "password1": "securepass",
            "password2": "securepass",
            "first_name": "Test"
        }
        response = self.client.get("/")
        request = response.wsgi_request
        form = CustomSignupForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save(request)
        self.assertIsInstance(user, User)
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.email, "test@example.com")
