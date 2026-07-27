"""Custom admin backend that bridges kit RBAC permissions into Django admin."""

from django.contrib.auth.backends import BaseBackend


class RbacAdminBackend(BaseBackend):
    """Django admin access backend powered by the kit RBAC module.

    Superusers always have access. Non-superusers must hold the
    ``admin:access`` permission through the RBAC module.
    """

    def has_module_perms(self, user_obj, app_label):
        return self._is_admin(user_obj)

    def has_perm(self, user_obj, perm, obj=None):
        return self._is_admin(user_obj)

    def _is_admin(self, user_obj):
        if not user_obj.is_active:
            return False
        if user_obj.is_superuser:
            return True
        from backend.core.container import get_container

        result = get_container().rbac.queries.check_user_permission.execute(
            user_id=user_obj.id,
            permission="admin:access",
        )
        return result["has_permission"]
