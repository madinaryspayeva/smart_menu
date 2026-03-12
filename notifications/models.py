# notifications/models.py

from django.contrib.auth import get_user_model
from django.db import models

from app.models import TimestampedModel
from notifications.choices import Notification_Type

User = get_user_model()

class Notification(TimestampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(
        max_length=20,
        choices=Notification_Type.choices,
        default=Notification_Type.INFO
    )
    is_read = models.BooleanField(default=False)
    link = models.CharField(
        max_length=500, 
        blank=True, 
        null=True
    )

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user} - {self.title}"