import pytest
from users.models import User

@pytest.mark.django_db
class TestUserModel:

    def test_create_user_success(self):
        manager = User.objects
        email = "TestUser@Example.com"
        password = "securepass"
        user = manager.create_user(email, password)

        assert isinstance(user, User)
        assert user.email == email.lower()
        assert user.check_password(password)
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_without_email_raises_value_error(self):
        with pytest.raises(ValueError, match="The email must be set"):
            User.objects.create_user(email=None, password="123")

    def test_create_superuser_success(self):
        manager = User.objects
        email = "admin@example.com"
        password = "adminpass"
        superuser = manager.create_superuser(email, password)

        assert isinstance(superuser, User)
        assert superuser.email == email.lower()
        assert superuser.check_password(password)
        assert superuser.is_staff
        assert superuser.is_superuser

    def test_create_superuser_with_is_staff_false_raises_value_error(self):
        with pytest.raises(ValueError, match="Superuser must have is_staff=True"):
            User.objects.create_superuser(email="admin@example.com", password="adminpass", is_staff=False)

    def test_create_superuser_with_is_superuser_false_raises_value_error(self):
        with pytest.raises(ValueError, match="Superuser must have is_superuser=True"):
            User.objects.create_superuser(email="admin@example.com", password="adminpass", is_superuser=False)

    def test_user_avatar_field(self, owner):
        assert not owner.avatar

    def test_user_str_returns_email(self, owner):
        assert str(owner) == owner.email
