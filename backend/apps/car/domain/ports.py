"""Inbound ports for cross-module collaborators used by the car module."""

from typing import Any, Protocol


class OwnerFacade(Protocol):
    """Port used by the car module to validate owner existence.

    The concrete implementation is normally the owner module's use-case facade,
    looked up through the use-case registry. Injecting it as a port keeps the
    car module's domain free of registry imports.
    """

    def get_owner_by_id(self, owner_id: int) -> Any: ...
