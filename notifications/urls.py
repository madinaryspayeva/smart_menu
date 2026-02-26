# notifications/urls.py

from django.urls import path

from .views import MarkNotificationReadView, NotificationListView

urlpatterns = [
    path("", NotificationListView.as_view(), name="notifications"),
    path("<uuid:pk>/read/", MarkNotificationReadView.as_view(), name="notification-read"),
]