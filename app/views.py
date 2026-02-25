from django.contrib.auth.mixins import LoginRequiredMixin

from app import settings


class AuthRequiredView(LoginRequiredMixin):
    login_url = settings.LOGIN_URL
    redirect_field_name = "next"
