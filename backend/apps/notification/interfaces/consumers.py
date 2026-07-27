"""WebSocket consumers for notification.

This is the kit's reference WebSocket delivery layer. Consumers are an
``interfaces/`` concern — the same layer as DRF views — so they may call use
cases but must not contain business logic themselves.
"""

import json

from channels.generic.websocket import AsyncWebsocketConsumer


def user_group(user_id):
    """Channel-layer group carrying one user's notifications."""
    return f"notifications.user.{user_id}"


class NotificationConsumer(AsyncWebsocketConsumer):
    """Push notifications to a single authenticated user.

    Anonymous connections are rejected outright — a socket is an authenticated
    surface exactly like the REST API. Server-side publishers reach a user by
    sending a ``notification.message`` event to :func:`user_group`.
    """

    async def connect(self):
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            await self.close(code=4401)
            return

        self.group_name = user_group(user.id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        group_name = getattr(self, "group_name", None)
        if group_name is not None:
            await self.channel_layer.group_discard(group_name, self.channel_name)

    async def notification_message(self, event):
        await self.send(text_data=json.dumps(event["payload"]))
