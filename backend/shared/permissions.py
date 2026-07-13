"""Shared permission helpers."""

from rest_framework import permissions

from backend.shared.use_case_registry import registry


class IsAdmin(permissions.BasePermission):
    """Allows access only to admin users."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


def rbac_permission(permission_name: str):
    """Factory returning a DRF permission class for an RBAC permission name.

    Staff users bypass the RBAC check. The permission class queries the
    rbac module through the use-case registry.
    """

    class _RbacPermission(permissions.BasePermission):
        def has_permission(self, request, view):
            if not request.user or not request.user.is_authenticated:
                return False
            if request.user.is_staff:
                return True
            rbac = registry.get("rbac")
            return rbac.queries.check_user_permission.execute(
                user_id=request.user.id,
                permission=permission_name,
            )

    return _RbacPermission
