# notifications/urls.py

from django.urls import path

from .views import DeleteNotificationView, MarkNotificationReadView, NotificationListView

urlpatterns = [
    path("", NotificationListView.as_view(), name="notifications"),
    path("<uuid:pk>/read/", MarkNotificationReadView.as_view(), name="notification-read"),
    path("<uuid:pk>/delete/", DeleteNotificationView.as_view(), name="notification-delete"),
]