from django.contrib.auth.forms import UserCreationForm
from users.models import User
from django import forms


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
