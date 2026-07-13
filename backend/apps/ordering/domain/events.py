"""Ordering domain events."""

from dataclasses import dataclass
from typing import ClassVar

from backend.shared.domain import DomainEvent


@dataclass
class OrderCreated(DomainEvent):
    event_type: ClassVar[str] = "ordering.order_created"


@dataclass
class JobStatusChanged(DomainEvent):
    event_type: ClassVar[str] = "ordering.job_status_changed"
