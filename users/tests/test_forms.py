import pytest
from users.models import User
from users.forms import CustomSignupForm

@pytest.mark.django_db
class TestCustomSignupForm:

    def test_first_name_field_required(self):
        form_data = {
            "email": "test@example.com",
            "password1": "securepass",
            "password2": "securepass",
        }
        form = CustomSignupForm(data=form_data)
        assert not form.is_valid()
        assert "first_name" in form.errors

    def test_form_valid_with_all_fields(self):
        form_data = {
            "email": "test@example.com",
            "password1": "securepass",
            "password2": "securepass",
            "first_name": "Test"
        }
        form = CustomSignupForm(data=form_data)
        assert form.is_valid()

    def test_save_creates_user_with_first_name(self, client):
        form_data = {
            "email": "test@example.com",
            "password1": "securepass",
            "password2": "securepass",
            "first_name": "Test"
        }
 
        response = client.get("/")
        request = response.wsgi_request

        form = CustomSignupForm(data=form_data)
        assert form.is_valid()
        user = form.save(request)
        assert isinstance(user, User)
        assert user.first_name == "Test"
        assert user.email == "test@example.com"
