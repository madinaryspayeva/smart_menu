import uuid

from behaviors.behaviors import Timestamped

from django.contrib.contenttypes.models import ContentType
from django.db import models

__all__ = [
    'models',
    'DefaultModel',
    'TimestampedModel',
]


class DefaultModel(models.Model):
    id = models.UUIDField(
         primary_key=True,
         default=uuid.uuid4,
         editable=False
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        """Default name for all models"""
        if hasattr(self, 'name'):
            return str(self.name)

        return super().__str__()

    @classmethod
    def get_contenttype(cls) -> ContentType:
        return ContentType.objects.get_for_model(cls)

    def update_from_kwargs(self, **kwargs):
        """A shortcut method to update model instance from the kwargs.
        """
        for (key, value) in kwargs.items():
            setattr(self, key, value)

    def setattr_and_save(self, key, value):
        """Shortcut for testing -- set attribute of the model and save"""
        setattr(self, key, value)
        self.save()

    @classmethod
    def get_label(cls) -> str:
        """Get a unique within the app model label
        """
        return cls._meta.label_lower.split('.')[-1]


class TimestampedModel(DefaultModel, Timestamped):
    """
    Default app model that has `created` and `updated` attributes.
    Currently based on https://github.com/audiolion/django-behaviors
    """
    class Meta:
        abstract = True
