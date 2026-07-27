"""Owner domain events.

Cross-module events are defined in ``backend.shared.events`` and re-exported
here so the rest of the owner module can import them from a local namespace.
"""

from backend.shared.events import OwnerCreated

__all__ = ["OwnerCreated"]
