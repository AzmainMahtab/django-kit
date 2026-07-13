"""RBAC domain events."""

from dataclasses import dataclass
from typing import ClassVar

from backend.shared.domain import DomainEvent


@dataclass
class PermissionCreated(DomainEvent):
    event_type: ClassVar[str] = "rbac.permission_created"


@dataclass
class RoleCreated(DomainEvent):
    event_type: ClassVar[str] = "rbac.role_created"


@dataclass
class RoleAssigned(DomainEvent):
    event_type: ClassVar[str] = "rbac.role_assigned"


@dataclass
class RoleRevoked(DomainEvent):
    event_type: ClassVar[str] = "rbac.role_revoked"


@dataclass
class PermissionAssignedToRole(DomainEvent):
    event_type: ClassVar[str] = "rbac.permission_assigned_to_role"


@dataclass
class PermissionRevokedFromRole(DomainEvent):
    event_type: ClassVar[str] = "rbac.permission_revoked_from_role"
