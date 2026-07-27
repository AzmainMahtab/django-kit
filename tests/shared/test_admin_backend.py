"""Tests for the RBAC admin backend."""

import pytest

from backend.apps.identity.domain.models import User
from backend.apps.rbac.domain.models import Permission, Role
from backend.shared.admin_backend import RbacAdminBackend

pytestmark = pytest.mark.django_db


def _permission(name):
    return Permission.objects.create(name=name, resource="admin", action="access")


def _role_with_permission(permission):
    role = Role.objects.create(name="admin")
    role.permissions.add(permission)
    return role


def test_superuser_has_admin_access():
    user = User.objects.create_user(
        username="super", email="super@example.com", password="secret123", is_superuser=True
    )
    backend = RbacAdminBackend()
    assert backend.has_module_perms(user, "admin") is True
    assert backend.has_perm(user, "admin.view_user") is True


def test_inactive_user_denied():
    user = User.objects.create_user(
        username="inactive",
        email="inactive@example.com",
        password="secret123",
        is_active=False,
    )
    backend = RbacAdminBackend()
    assert backend.has_module_perms(user, "admin") is False


def test_user_with_admin_access_permission_allowed():
    user = User.objects.create_user(
        username="admin", email="admin@example.com", password="secret123"
    )
    permission = _permission("admin:access")
    role = _role_with_permission(permission)
    role.user_roles.create(user_id=user.id)

    backend = RbacAdminBackend()
    assert backend.has_module_perms(user, "admin") is True


def test_user_without_admin_access_permission_denied():
    user = User.objects.create_user(
        username="normal", email="normal@example.com", password="secret123"
    )
    backend = RbacAdminBackend()
    assert backend.has_module_perms(user, "admin") is False
