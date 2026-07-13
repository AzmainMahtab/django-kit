"""Shared DTOs and value objects."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


class Money(Decimal):
    """All monetary values MUST use this. Backed by DecimalField in DB."""

    pass


@dataclass(frozen=True)
class AddressDTO:
    id: Optional[int] = None
    name: str = ""
    company: str = ""
    attention: str = ""
    address1: str = ""
    address2: str = ""
    city: str = ""
    state: str = ""
    state_code: str = ""
    zip_code: str = ""
    country: str = "US"


@dataclass(frozen=True)
class UserDTO:
    id: int
    username: str
    email: str
    first_name: str = ""
    last_name: str = ""
    is_staff: bool = False
    is_active: bool = True


@dataclass(frozen=True)
class JobDTO:
    id: int
    job_id: str
    job_status: str
    file_editable: bool
    order_id: int


@dataclass(frozen=True)
class OrderDTO:
    id: int
    order_number: str
    user_id: int
    status: str
    jobs: list[JobDTO]
