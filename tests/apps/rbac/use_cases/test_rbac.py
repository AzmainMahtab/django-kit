"""Unit tests for RBAC use cases."""

from datetime import UTC, datetime

import pytest

from backend.apps.rbac.domain.models import Permission, Role
from backend.apps.rbac.domain.repository_interfaces import RbacRepositoryInterface
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
from backend.shared.exceptions import BusinessValidationError, NotFoundError

pytestmark = pytest.mark.django_db


class MockRbacRepository(RbacRepositoryInterface):
    def __init__(self):
        self._permissions: dict[int, Permission] = {}
        self._roles: dict[int, Role] = {}
        self._role_permissions: set[tuple[int, int]] = set()
        self._user_roles: dict[int, set[int]] = {}
        self._next_permission_id = 1
        self._next_role_id = 1

    def create_permission(
        self,
        name: str,
        resource: str,
        action: str,
        description: str = "",
    ) -> Permission:
        permission = Permission(
            id=self._next_permission_id,
            name=name,
            resource=resource,
            action=action,
            description=description,
            created_at=datetime.now(UTC),
        )
        self._permissions[permission.id] = permission
        self._next_permission_id += 1
        return permission

    def get_permission_by_id(self, permission_id: int) -> Permission:
        if permission_id not in self._permissions:
            raise Permission.DoesNotExist
        return self._permissions[permission_id]

    def list_permissions(self):
        return sorted(self._permissions.values(), key=lambda p: p.name)

    def create_role(self, name: str, description: str = "") -> Role:
        role = Role(
            id=self._next_role_id,
            name=name,
            description=description,
            created_at=datetime.now(UTC),
        )
        self._roles[role.id] = role
        self._next_role_id += 1
        return role

    def get_role_by_id(self, role_id: int) -> Role:
        if role_id not in self._roles:
            raise Role.DoesNotExist
        return self._roles[role_id]

    def list_roles(self):
        return sorted(self._roles.values(), key=lambda r: r.name)

    def assign_role_to_user(
        self,
        user_id: int,
        role_id: int,
        assigned_by_id: int | None = None,
    ) -> None:
        self._user_roles.setdefault(user_id, set()).add(role_id)

    def revoke_role_from_user(self, user_id: int, role_id: int) -> None:
        self._user_roles.get(user_id, set()).discard(role_id)

    def assign_permission_to_role(
        self,
        role_id: int,
        permission_id: int,
        assigned_by_id: int | None = None,
    ) -> None:
        self._role_permissions.add((role_id, permission_id))

    def revoke_permission_from_role(self, role_id: int, permission_id: int) -> None:
        self._role_permissions.discard((role_id, permission_id))

    def get_user_roles(self, user_id: int):
        role_ids = self._user_roles.get(user_id, set())
        return [self._roles[rid] for rid in role_ids]

    def get_user_permissions(self, user_id: int):
        role_ids = self._user_roles.get(user_id, set())
        permission_ids = {
            pid for rid, pid in self._role_permissions if rid in role_ids
        }
        return [self._permissions[pid] for pid in permission_ids]

    def check_user_permission(self, user_id: int, permission_name: str) -> bool:
        return any(
            p.name == permission_name for p in self.get_user_permissions(user_id)
        )

    def check_user_role(self, user_id: int, role_name: str) -> bool:
        return any(r.name == role_name for r in self.get_user_roles(user_id))

    def check_permission_on_role(self, role_id: int, permission_id: int) -> bool:
        return (role_id, permission_id) in self._role_permissions


@pytest.fixture
def user():
    from backend.apps.identity.domain.models import User

    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="secret123",
        is_active=True,
    )


def test_create_permission_success():
    repo = MockRbacRepository()
    use_case = CreatePermissionUseCase(rbac_repository=repo)

    result = use_case.execute(
        name="user:create",
        resource="user",
        action="create",
        description="Create users",
    )

    assert result.name == "user:create"
    assert result.resource == "user"
    assert result.action == "create"


def test_create_permission_duplicate_raises():
    repo = MockRbacRepository()
    use_case = CreatePermissionUseCase(rbac_repository=repo)
    use_case.execute(name="user:create", resource="user", action="create")

    with pytest.raises(BusinessValidationError) as exc:
        use_case.execute(name="user:create", resource="user", action="create")

    assert "already exists" in str(exc.value)


def test_list_permissions():
    repo = MockRbacRepository()
    repo.create_permission(name="user:create", resource="user", action="create")
    repo.create_permission(name="user:delete", resource="user", action="delete")

    use_case = ListPermissionsUseCase(rbac_repository=repo)
    result = use_case.execute()

    assert len(result) == 2
    assert result[0]["name"] == "user:create"
    assert result[1]["name"] == "user:delete"


def test_create_role_success():
    repo = MockRbacRepository()
    use_case = CreateRoleUseCase(rbac_repository=repo)

    result = use_case.execute(name="admin", description="Administrator")

    assert result.name == "admin"
    assert result.description == "Administrator"


def test_create_role_duplicate_raises():
    repo = MockRbacRepository()
    use_case = CreateRoleUseCase(rbac_repository=repo)
    use_case.execute(name="admin")

    with pytest.raises(BusinessValidationError) as exc:
        use_case.execute(name="admin")

    assert "already exists" in str(exc.value)


def test_get_role_success():
    repo = MockRbacRepository()
    role = repo.create_role(name="editor")
    use_case = GetRoleUseCase(rbac_repository=repo)

    result = use_case.execute(role_id=role.id)

    assert result["id"] == role.id
    assert result["name"] == "editor"


def test_get_role_not_found():
    use_case = GetRoleUseCase(rbac_repository=MockRbacRepository())

    with pytest.raises(NotFoundError):
        use_case.execute(role_id=999)


def test_assign_and_revoke_role_to_user(user):
    repo = MockRbacRepository()
    role = repo.create_role(name="admin")
    assign = AssignRoleToUserUseCase(rbac_repository=repo)
    assign.execute(user_id=user.id, role_id=role.id)

    assert repo.check_user_role(user.id, "admin") is True

    revoke = RevokeRoleFromUserUseCase(rbac_repository=repo)
    revoke.execute(user_id=user.id, role_id=role.id)

    assert repo.check_user_role(user.id, "admin") is False


def test_assign_role_already_assigned_raises(user):
    repo = MockRbacRepository()
    role = repo.create_role(name="admin")
    assign = AssignRoleToUserUseCase(rbac_repository=repo)
    assign.execute(user_id=user.id, role_id=role.id)

    with pytest.raises(BusinessValidationError):
        assign.execute(user_id=user.id, role_id=role.id)


def test_revoke_role_not_assigned_raises(user):
    repo = MockRbacRepository()
    role = repo.create_role(name="admin")
    revoke = RevokeRoleFromUserUseCase(rbac_repository=repo)

    with pytest.raises(BusinessValidationError):
        revoke.execute(user_id=user.id, role_id=role.id)


def test_assign_and_revoke_permission_to_role():
    repo = MockRbacRepository()
    role = repo.create_role(name="admin")
    permission = repo.create_permission(name="user:create", resource="user", action="create")
    assign = AssignPermissionToRoleUseCase(rbac_repository=repo)
    assign.execute(role_id=role.id, permission_id=permission.id)

    assert repo.check_permission_on_role(role.id, permission.id) is True

    revoke = RevokePermissionFromRoleUseCase(rbac_repository=repo)
    revoke.execute(role_id=role.id, permission_id=permission.id)

    assert repo.check_permission_on_role(role.id, permission.id) is False


def test_get_user_permissions(user):
    repo = MockRbacRepository()
    role = repo.create_role(name="admin")
    permission = repo.create_permission(name="user:create", resource="user", action="create")
    repo.assign_permission_to_role(role.id, permission.id)
    repo.assign_role_to_user(user_id=user.id, role_id=role.id)

    use_case = GetUserPermissionsUseCase(rbac_repository=repo)
    result = use_case.execute(user_id=user.id)

    assert len(result) == 1
    assert result[0]["name"] == "user:create"


def test_get_user_roles(user):
    repo = MockRbacRepository()
    role = repo.create_role(name="admin")
    repo.assign_role_to_user(user_id=user.id, role_id=role.id)

    use_case = GetUserRolesUseCase(rbac_repository=repo)
    result = use_case.execute(user_id=user.id)

    assert len(result) == 1
    assert result[0]["name"] == "admin"


def test_check_user_permission(user):
    repo = MockRbacRepository()
    role = repo.create_role(name="admin")
    permission = repo.create_permission(name="user:create", resource="user", action="create")
    repo.assign_permission_to_role(role.id, permission.id)
    repo.assign_role_to_user(user_id=user.id, role_id=role.id)

    use_case = CheckUserPermissionUseCase(rbac_repository=repo)
    result = use_case.execute(user_id=user.id, permission="user:create")

    assert result["has_permission"] is True

    result = use_case.execute(user_id=user.id, permission="user:delete")
    assert result["has_permission"] is False
