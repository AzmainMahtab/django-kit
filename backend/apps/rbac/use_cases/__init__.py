"""Public API for the RBAC module.

★ THIS IS THE ONLY FILE OTHER MODULES CAN IMPORT FROM THIS APP ★
"""

from backend.apps.rbac.use_cases.commands.assign_permission_to_role import (
    AssignPermissionToRoleUseCase,
)
from backend.apps.rbac.use_cases.commands.assign_role_to_user import AssignRoleToUserUseCase
from backend.apps.rbac.use_cases.commands.create_permission import CreatePermissionUseCase
from backend.apps.rbac.use_cases.commands.create_role import CreateRoleUseCase
from backend.apps.rbac.use_cases.commands.revoke_permission_from_role import (
    RevokePermissionFromRoleUseCase,
)
from backend.apps.rbac.use_cases.commands.revoke_role_from_user import RevokeRoleFromUserUseCase
from backend.apps.rbac.use_cases.queries.check_user_permission import CheckUserPermissionUseCase
from backend.apps.rbac.use_cases.queries.get_role import GetRoleUseCase
from backend.apps.rbac.use_cases.queries.get_user_permissions import GetUserPermissionsUseCase
from backend.apps.rbac.use_cases.queries.get_user_roles import GetUserRolesUseCase
from backend.apps.rbac.use_cases.queries.list_permissions import ListPermissionsUseCase
from backend.apps.rbac.use_cases.queries.list_roles import ListRolesUseCase


class RbacUseCases:
    """Facade exposed through the use-case registry."""

    def __init__(self):
        self.commands = RbacCommands()
        self.queries = RbacQueries()

    def create_permission(self, **kwargs):
        return self.commands.create_permission.execute(**kwargs)

    def create_role(self, **kwargs):
        return self.commands.create_role.execute(**kwargs)

    def assign_role_to_user(self, **kwargs):
        return self.commands.assign_role_to_user.execute(**kwargs)

    def revoke_role_from_user(self, **kwargs):
        return self.commands.revoke_role_from_user.execute(**kwargs)

    def assign_permission_to_role(self, **kwargs):
        return self.commands.assign_permission_to_role.execute(**kwargs)

    def revoke_permission_from_role(self, **kwargs):
        return self.commands.revoke_permission_from_role.execute(**kwargs)

    def list_permissions(self, **kwargs):
        return self.queries.list_permissions.execute(**kwargs)

    def list_roles(self, **kwargs):
        return self.queries.list_roles.execute(**kwargs)

    def get_role(self, **kwargs):
        return self.queries.get_role.execute(**kwargs)

    def get_user_permissions(self, **kwargs):
        return self.queries.get_user_permissions.execute(**kwargs)

    def get_user_roles(self, **kwargs):
        return self.queries.get_user_roles.execute(**kwargs)

    def check_user_permission(self, **kwargs):
        return self.queries.check_user_permission.execute(**kwargs)


class RbacCommands:
    def __init__(self):
        self.create_permission = CreatePermissionUseCase()
        self.create_role = CreateRoleUseCase()
        self.assign_role_to_user = AssignRoleToUserUseCase()
        self.revoke_role_from_user = RevokeRoleFromUserUseCase()
        self.assign_permission_to_role = AssignPermissionToRoleUseCase()
        self.revoke_permission_from_role = RevokePermissionFromRoleUseCase()


class RbacQueries:
    def __init__(self):
        self.list_permissions = ListPermissionsUseCase()
        self.list_roles = ListRolesUseCase()
        self.get_role = GetRoleUseCase()
        self.get_user_permissions = GetUserPermissionsUseCase()
        self.get_user_roles = GetUserRolesUseCase()
        self.check_user_permission = CheckUserPermissionUseCase()
