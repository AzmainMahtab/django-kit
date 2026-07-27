"""Cross-module event contracts.

Publishing modules define concrete subclasses here or in their own
public events module. Subscribing modules import only this module,
never the publisher's domain.
"""

from dataclasses import dataclass
from typing import ClassVar

from backend.shared.domain import DomainEvent


@dataclass
class CarCreated(DomainEvent):
    event_type: ClassVar[str] = "car.car_created"


@dataclass
class OwnerCreated(DomainEvent):
    event_type: ClassVar[str] = "owner.owner_created"


@dataclass
class OrderCreated(DomainEvent):
    event_type: ClassVar[str] = "ordering.order_created"


@dataclass
class JobStatusChanged(DomainEvent):
    event_type: ClassVar[str] = "ordering.job_status_changed"
