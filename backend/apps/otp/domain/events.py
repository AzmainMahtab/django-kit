"""OTP domain events."""

from dataclasses import dataclass
from typing import ClassVar

from backend.shared.domain import DomainEvent


@dataclass
class OtpGenerated(DomainEvent):
    event_type: ClassVar[str] = "otp.generated"


@dataclass
class OtpValidated(DomainEvent):
    event_type: ClassVar[str] = "otp.validated"
