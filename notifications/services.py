from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from notifications.choices import Notification_Type
from notifications.models import Notification


class NotificationService:

    @staticmethod
    def send(user, title, message, type=Notification_Type.INFO, save=True):
        channel_layer = get_channel_layer()
        
        if save:
            notification = Notification.objects.create(
                user=user,
                title=title,
                message=message,
                type=type,
            )
            notification_id = str(notification.id)
            is_read = notification.is_read
            created = notification.created.isoformat()
        else:
            notification_id = None
            is_read = None
            created = None

        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                "type": "notify",
                "data": {
                    "id": notification_id,
                    "title": title,
                    "message": message,
                    "type": type,
                    "created": created,
                    "is_read": is_read,
                    "save": save,
                },
            },
        )

        return notification if save else None