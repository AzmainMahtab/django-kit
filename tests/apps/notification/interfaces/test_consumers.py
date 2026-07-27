"""Tests for the notification WebSocket consumer."""

import pytest
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator

from backend.apps.identity.domain.models import User
from backend.apps.notification.interfaces.consumers import NotificationConsumer, user_group


@database_sync_to_async
def _create_user():
    return User.objects.create_user(
        username="socket", email="socket@example.com", password="secret123"
    )


def _communicator(user=None):
    communicator = WebsocketCommunicator(NotificationConsumer.as_asgi(), "/ws/notifications/")
    if user is not None:
        communicator.scope["user"] = user
    return communicator


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_anonymous_connection_is_rejected():
    communicator = _communicator()
    connected, _ = await communicator.connect()

    assert connected is False
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_authenticated_user_receives_their_notifications():
    user = await _create_user()
    communicator = _communicator(user)
    connected, _ = await communicator.connect()
    assert connected is True

    await get_channel_layer().group_send(
        user_group(user.id),
        {"type": "notification.message", "payload": {"id": 1, "message": "order shipped"}},
    )

    assert await communicator.receive_json_from() == {"id": 1, "message": "order shipped"}
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_a_user_does_not_receive_another_users_notifications():
    user = await _create_user()
    communicator = _communicator(user)
    await communicator.connect()

    await get_channel_layer().group_send(
        user_group(user.id + 999),
        {"type": "notification.message", "payload": {"id": 2, "message": "not yours"}},
    )

    assert await communicator.receive_nothing() is True
    await communicator.disconnect()
