"""WebSocket URL routing for notification."""

from django.urls import path

from backend.apps.notification.interfaces.consumers import NotificationConsumer

websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
