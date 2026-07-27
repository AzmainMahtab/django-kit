"""Car domain events.

Cross-module events are defined in ``backend.shared.events`` and re-exported
here so the rest of the car module can import them from a local namespace.
"""

from backend.shared.events import CarCreated

__all__ = ["CarCreated"]
