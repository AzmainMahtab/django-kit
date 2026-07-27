"""Project-level WebSocket routing.

The composition root for sockets: each bounded context contributes its own
``interfaces/routing.py`` and they are combined here, mirroring how
``core/urls.py`` combines the HTTP urlconfs.
"""

from backend.apps.notification.interfaces.routing import (
    websocket_urlpatterns as notification_websocket_urlpatterns,
)

websocket_urlpatterns = [
    *notification_websocket_urlpatterns,
]
