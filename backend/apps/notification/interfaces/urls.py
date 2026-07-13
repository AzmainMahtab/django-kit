"""Notification URL configuration."""

from django.urls import path

from backend.apps.notification.interfaces.views import NotificationListView

urlpatterns = [
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
]
