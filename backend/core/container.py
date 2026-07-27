"""Typed dependency container. Built once at process start."""

from functools import partial

from backend.apps.car.use_cases import CarUseCases
from backend.apps.identity.use_cases import IdentityUseCases
from backend.apps.notification.infrastructure.event_handlers import on_job_status_changed
from backend.apps.notification.use_cases import NotificationUseCases
from backend.apps.ordering.use_cases import OrderingUseCases
from backend.apps.otp.use_cases import OtpUseCases
from backend.apps.owner.use_cases import OwnerUseCases
from backend.apps.rbac.use_cases import RbacUseCases
from backend.shared.event_bus import EventBus, _outbox_publish
from backend.shared.events import JobStatusChanged


class AppContainer:
    """Wires every use-case facade with its real dependencies."""

    def __init__(self) -> None:
        self.event_bus = EventBus(durable_publisher=_outbox_publish)

        # Modules that only publish/consume events need the bus.
        self.identity = IdentityUseCases(event_bus=self.event_bus)
        self.otp = OtpUseCases(event_bus=self.event_bus)
        self.rbac = RbacUseCases(event_bus=self.event_bus)
        self.owner = OwnerUseCases(event_bus=self.event_bus)
        self.car = CarUseCases(
            event_bus=self.event_bus,
            owner_facade=self.owner,
        )
        self.ordering = OrderingUseCases(event_bus=self.event_bus)
        self.notification = NotificationUseCases(event_bus=self.event_bus)

        # Register cross-module event subscribers on the injected bus.
        self._register_event_handlers()

    def _register_event_handlers(self) -> None:
        self.event_bus.subscribe(
            JobStatusChanged.event_type,
            partial(on_job_status_changed, self.notification),
        )


# Process-level singleton, constructed lazily so imports remain cheap.
_container: AppContainer | None = None


def get_container() -> AppContainer:
    global _container
    if _container is None:
        _container = AppContainer()
    return _container


def reset_container() -> None:
    """Reset for tests."""
    global _container
    _container = None
