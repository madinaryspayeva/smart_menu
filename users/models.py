
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import TimestampedModel
from users.managers import UserManager
from users.media_path import user_avatar_upload_path


class User(AbstractUser, TimestampedModel):
    email = models.EmailField(
        _('Email address'),
        unique=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    username = None
    avatar = models.ImageField(
        upload_to=user_avatar_upload_path, 
        blank=True, 
        null=True, 
        verbose_name=_('Аватарка')
    )

    objects = UserManager()

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
