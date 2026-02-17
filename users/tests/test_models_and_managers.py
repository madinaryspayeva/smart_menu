from django.test import TestCase
from django.core.exceptions import ValidationError
from users.models import User


class UserModelAndManagerTests(TestCase):

    def setUp(self):
        self.manager = User.objects
    
    def test_create_user_success(self):
        """Создание обычного пользователя через менеджер"""

        email = "TestUser@Example.com"
        password = "securepass"
        user = self.manager.create_user(email, password)

        self.assertIsInstance(user, User)
        self.assertEqual(user.email, email.lower())
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_user_without_email_raises_value_error(self):
        """Создание пользователя без email вызывает ошибку ValueError"""

        with self.assertRaisesMessage(ValueError, "The email must be set"):
            self.manager.create_user(email=None, password="123")
    
    def test_create_superuser_success(self):
        """Создание суперпользователя через менеджер"""

        email = "admin@example.com"
        password = "adminpass"
        superuser = self.manager.create_superuser(email, password)

        self.assertIsInstance(superuser, User)
        self.assertEqual(superuser.email, email.lower())
        self.assertTrue(superuser.check_password(password))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
    
    def test_creste_superuser_with_is_staff_false_raises_value_error(self):
        """Создание суперпользователя с is_staff=False вызывает ошибку ValueError"""

        with self.assertRaisesMessage(ValueError, "Superuser must have is_staff=True"):
            self.manager.create_superuser(email="admin@example.com", password="adminpass", is_staff=False)
    
    def test_create_superuser_with_is_superuser_false_raises_value_error(self):
        """Создание суперпользователя с is_superuser=False вызывает ошибку ValueError"""

        with self.assertRaisesMessage(ValueError, "Superuser must have is_superuser=True"):
            self.manager.create_superuser(email="admin@example.com", password="adminpass", is_superuser=False)

    def test_user_avatar_field(self):
        """Проверка поля avatar на пустое значение"""

        user = self.manager.create_user(email="TestUser@Example.com", password="securepass")
        self.assertFalse(user.avatar)

    def test_user_str_returns_email(self):
        """Проверка метода __str__ модели User"""

        user = self.manager.create_user(email="TestUser@Example.com", password="securepass")
        self.assertEqual(str(user), user.email)
