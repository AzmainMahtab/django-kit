"""Unit tests for RBAC use cases."""

import pytest

from backend.apps.identity.domain.models import User
from backend.apps.rbac.domain.models import Permission, Role
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
from backend.shared.event_bus import EventBus
from backend.shared.exceptions import BusinessValidationError, NotFoundError

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="secret123",
        is_active=True,
    )


def test_create_permission_success():
    bus = EventBus()
    use_case = CreatePermissionUseCase(event_bus=bus)

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
    bus = EventBus()
    use_case = CreatePermissionUseCase(event_bus=bus)
    use_case.execute(name="user:create", resource="user", action="create")

    with pytest.raises(BusinessValidationError) as exc:
        use_case.execute(name="user:create", resource="user", action="create")

    assert "already exists" in str(exc.value)


def test_list_permissions():
    Permission.objects.create(name="user:create", resource="user", action="create")
    Permission.objects.create(name="user:delete", resource="user", action="delete")

    use_case = ListPermissionsUseCase()
    result = use_case.execute()

    assert len(result) == 2
    assert result[0]["name"] == "user:create"
    assert result[1]["name"] == "user:delete"


def test_create_role_success():
    bus = EventBus()
    use_case = CreateRoleUseCase(event_bus=bus)

    result = use_case.execute(name="admin", description="Administrator")

    assert result.name == "admin"
    assert result.description == "Administrator"


def test_create_role_duplicate_raises():
    bus = EventBus()
    use_case = CreateRoleUseCase(event_bus=bus)
    use_case.execute(name="admin")

    with pytest.raises(BusinessValidationError) as exc:
        use_case.execute(name="admin")

    assert "already exists" in str(exc.value)


def test_get_role_success():
    role = Role.objects.create(name="editor")
    use_case = GetRoleUseCase()

    result = use_case.execute(role_id=role.id)

    assert result["id"] == role.id
    assert result["name"] == "editor"


def test_get_role_not_found():
    use_case = GetRoleUseCase()

    with pytest.raises(NotFoundError):
        use_case.execute(role_id=999)


def test_assign_and_revoke_role_to_user(user):
    role = Role.objects.create(name="admin")
    bus = EventBus()
    assign = AssignRoleToUserUseCase(event_bus=bus)
    assign.execute(user_id=user.id, role_id=role.id)

    assert role.user_roles.filter(user_id=user.id).exists()

    revoke = RevokeRoleFromUserUseCase(event_bus=bus)
    revoke.execute(user_id=user.id, role_id=role.id)

    assert not role.user_roles.filter(user_id=user.id).exists()


def test_assign_role_already_assigned_raises(user):
    role = Role.objects.create(name="admin")
    bus = EventBus()
    assign = AssignRoleToUserUseCase(event_bus=bus)
    assign.execute(user_id=user.id, role_id=role.id)

    with pytest.raises(BusinessValidationError):
        assign.execute(user_id=user.id, role_id=role.id)


def test_revoke_role_not_assigned_raises(user):
    role = Role.objects.create(name="admin")
    bus = EventBus()
    revoke = RevokeRoleFromUserUseCase(event_bus=bus)

    with pytest.raises(BusinessValidationError):
        revoke.execute(user_id=user.id, role_id=role.id)


def test_assign_and_revoke_permission_to_role():
    role = Role.objects.create(name="admin")
    permission = Permission.objects.create(name="user:create", resource="user", action="create")
    bus = EventBus()
    assign = AssignPermissionToRoleUseCase(event_bus=bus)
    assign.execute(role_id=role.id, permission_id=permission.id)

    assert role.role_permissions.filter(permission_id=permission.id).exists()

    revoke = RevokePermissionFromRoleUseCase(event_bus=bus)
    revoke.execute(role_id=role.id, permission_id=permission.id)

    assert not role.role_permissions.filter(permission_id=permission.id).exists()


def test_get_user_permissions(user):
    role = Role.objects.create(name="admin")
    permission = Permission.objects.create(name="user:create", resource="user", action="create")
    role.permissions.add(permission)
    role.user_roles.create(user_id=user.id)

    use_case = GetUserPermissionsUseCase()
    result = use_case.execute(user_id=user.id)

    assert len(result) == 1
    assert result[0]["name"] == "user:create"


def test_get_user_roles(user):
    role = Role.objects.create(name="admin")
    role.user_roles.create(user_id=user.id)

    use_case = GetUserRolesUseCase()
    result = use_case.execute(user_id=user.id)

    assert len(result) == 1
    assert result[0]["name"] == "admin"


def test_check_user_permission(user):
    role = Role.objects.create(name="admin")
    permission = Permission.objects.create(name="user:create", resource="user", action="create")
    role.permissions.add(permission)
    role.user_roles.create(user_id=user.id)

    bus = EventBus()
    use_case = CheckUserPermissionUseCase()
    result = use_case.execute(user_id=user.id, permission="user:create")

    assert result["has_permission"] is True

    result = use_case.execute(user_id=user.id, permission="user:delete")
    assert result["has_permission"] is False
