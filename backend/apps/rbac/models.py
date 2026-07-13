"""Re-export RBAC domain models for Django discovery."""

from backend.apps.rbac.domain.models import Permission, Role, RolePermission, UserRole

__all__ = ["Permission", "Role", "RolePermission", "UserRole"]
