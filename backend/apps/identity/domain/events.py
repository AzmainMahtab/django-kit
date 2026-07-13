"""Identity domain events."""

from dataclasses import dataclass
from typing import ClassVar

from backend.shared.domain import DomainEvent


@dataclass
class UserCreated(DomainEvent):
    event_type: ClassVar[str] = "identity.user_created"


@dataclass
class UserUpdated(DomainEvent):
    event_type: ClassVar[str] = "identity.user_updated"


@dataclass
class UserDeleted(DomainEvent):
    event_type: ClassVar[str] = "identity.user_deleted"


@dataclass
class UserLoggedIn(DomainEvent):
    event_type: ClassVar[str] = "identity.user_logged_in"


@dataclass
class UserLoggedOut(DomainEvent):
    event_type: ClassVar[str] = "identity.user_logged_out"


@dataclass
class TokenRefreshed(DomainEvent):
    event_type: ClassVar[str] = "identity.token_refreshed"
