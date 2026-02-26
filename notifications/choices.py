from django.db import models


class Notification_Type(models.TextChoices):
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"
        INFO = "info", "Info"
