"""API integration tests for RBAC endpoints."""

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from backend.apps.identity.domain.models import User
from backend.apps.rbac.interfaces.views import (
    PermissionListCreateView,
    RoleDetailView,
    RoleListCreateView,
    RolePermissionAssignView,
    RoleUserAssignView,
    UserPermissionCheckView,
    UserPermissionListView,
    UserRoleListView,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def factory():
    return APIRequestFactory()


@pytest.fixture
def admin_user():
    return User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="secret123",
        is_staff=True,
        is_active=True,
    )


@pytest.fixture
def regular_user():
    return User.objects.create_user(
        username="regular",
        email="regular@example.com",
        password="secret123",
        is_active=True,
    )


def _auth_request(factory, method, user, view, url, data=None, kwargs=None):
    kwargs = kwargs or {}
    if method == "get":
        request = factory.get(url, data or {})
    elif method == "post":
        request = factory.post(url, data or {}, format="json")
    elif method == "delete":
        request = factory.delete(url, data or {}, format="json")
    else:
        raise ValueError(f"Unsupported method: {method}")
    force_authenticate(request, user=user)
    return view.as_view()(request, **kwargs)


def test_create_permission(factory, admin_user):
    response = _auth_request(
        factory,
        "post",
        admin_user,
        PermissionListCreateView,
        "/api/rbac/permissions/",
        {"name": "user:create", "resource": "user", "action": "create"},
    )
    assert response.status_code == 201
    assert response.data["name"] == "user:create"


def test_list_permissions(factory, admin_user):
    _auth_request(
        factory,
        "post",
        admin_user,
        PermissionListCreateView,
        "/api/rbac/permissions/",
        {"name": "user:create", "resource": "user", "action": "create"},
    )
    response = _auth_request(
        factory,
        "get",
        admin_user,
        PermissionListCreateView,
        "/api/rbac/permissions/",
    )
    assert response.status_code == 200
    assert len(response.data) == 1


def test_create_role(factory, admin_user):
    response = _auth_request(
        factory,
        "post",
        admin_user,
        RoleListCreateView,
        "/api/rbac/roles/",
        {"name": "admin", "description": "Admins"},
    )
    assert response.status_code == 201
    assert response.data["name"] == "admin"


def test_get_role(factory, admin_user):
    created = _auth_request(
        factory,
        "post",
        admin_user,
        RoleListCreateView,
        "/api/rbac/roles/",
        {"name": "admin"},
    )
    response = _auth_request(
        factory,
        "get",
        admin_user,
        RoleDetailView,
        f"/api/rbac/roles/{created.data['id']}/",
        kwargs={"role_id": created.data["id"]},
    )
    assert response.status_code == 200
    assert response.data["name"] == "admin"


def test_assign_permission_to_role(factory, admin_user):
    perm = _auth_request(
        factory,
        "post",
        admin_user,
        PermissionListCreateView,
        "/api/rbac/permissions/",
        {"name": "user:create", "resource": "user", "action": "create"},
    )
    role = _auth_request(
        factory,
        "post",
        admin_user,
        RoleListCreateView,
        "/api/rbac/roles/",
        {"name": "admin"},
    )
    response = _auth_request(
        factory,
        "post",
        admin_user,
        RolePermissionAssignView,
        f"/api/rbac/roles/{role.data['id']}/permissions/",
        {"permission_id": perm.data["id"]},
        kwargs={"role_id": role.data["id"]},
    )
    assert response.status_code == 200


def test_revoke_permission_from_role(factory, admin_user):
    perm = _auth_request(
        factory,
        "post",
        admin_user,
        PermissionListCreateView,
        "/api/rbac/permissions/",
        {"name": "user:create", "resource": "user", "action": "create"},
    )
    role = _auth_request(
        factory,
        "post",
        admin_user,
        RoleListCreateView,
        "/api/rbac/roles/",
        {"name": "admin"},
    )
    _auth_request(
        factory,
        "post",
        admin_user,
        RolePermissionAssignView,
        f"/api/rbac/roles/{role.data['id']}/permissions/",
        {"permission_id": perm.data["id"]},
        kwargs={"role_id": role.data["id"]},
    )
    response = _auth_request(
        factory,
        "delete",
        admin_user,
        RolePermissionAssignView,
        f"/api/rbac/roles/{role.data['id']}/permissions/",
        {"permission_id": perm.data["id"]},
        kwargs={"role_id": role.data["id"]},
    )
    assert response.status_code == 200


def test_assign_role_to_user(factory, admin_user, regular_user):
    role = _auth_request(
        factory,
        "post",
        admin_user,
        RoleListCreateView,
        "/api/rbac/roles/",
        {"name": "admin"},
    )
    response = _auth_request(
        factory,
        "post",
        admin_user,
        RoleUserAssignView,
        f"/api/rbac/roles/{role.data['id']}/users/",
        {"user_id": regular_user.id},
        kwargs={"role_id": role.data["id"]},
    )
    assert response.status_code == 200


def test_list_user_roles(factory, admin_user, regular_user):
    role = _auth_request(
        factory,
        "post",
        admin_user,
        RoleListCreateView,
        "/api/rbac/roles/",
        {"name": "admin"},
    )
    _auth_request(
        factory,
        "post",
        admin_user,
        RoleUserAssignView,
        f"/api/rbac/roles/{role.data['id']}/users/",
        {"user_id": regular_user.id},
        kwargs={"role_id": role.data["id"]},
    )
    response = _auth_request(
        factory,
        "get",
        admin_user,
        UserRoleListView,
        f"/api/rbac/users/{regular_user.id}/roles/",
        kwargs={"user_id": regular_user.id},
    )
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "admin"


def test_list_user_permissions(factory, admin_user, regular_user):
    perm = _auth_request(
        factory,
        "post",
        admin_user,
        PermissionListCreateView,
        "/api/rbac/permissions/",
        {"name": "user:create", "resource": "user", "action": "create"},
    )
    role = _auth_request(
        factory,
        "post",
        admin_user,
        RoleListCreateView,
        "/api/rbac/roles/",
        {"name": "admin"},
    )
    _auth_request(
        factory,
        "post",
        admin_user,
        RolePermissionAssignView,
        f"/api/rbac/roles/{role.data['id']}/permissions/",
        {"permission_id": perm.data["id"]},
        kwargs={"role_id": role.data["id"]},
    )
    _auth_request(
        factory,
        "post",
        admin_user,
        RoleUserAssignView,
        f"/api/rbac/roles/{role.data['id']}/users/",
        {"user_id": regular_user.id},
        kwargs={"role_id": role.data["id"]},
    )
    response = _auth_request(
        factory,
        "get",
        admin_user,
        UserPermissionListView,
        f"/api/rbac/users/{regular_user.id}/permissions/",
        kwargs={"user_id": regular_user.id},
    )
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "user:create"


def test_check_user_permission(factory, admin_user, regular_user):
    perm = _auth_request(
        factory,
        "post",
        admin_user,
        PermissionListCreateView,
        "/api/rbac/permissions/",
        {"name": "user:create", "resource": "user", "action": "create"},
    )
    role = _auth_request(
        factory,
        "post",
        admin_user,
        RoleListCreateView,
        "/api/rbac/roles/",
        {"name": "admin"},
    )
    _auth_request(
        factory,
        "post",
        admin_user,
        RolePermissionAssignView,
        f"/api/rbac/roles/{role.data['id']}/permissions/",
        {"permission_id": perm.data["id"]},
        kwargs={"role_id": role.data["id"]},
    )
    _auth_request(
        factory,
        "post",
        admin_user,
        RoleUserAssignView,
        f"/api/rbac/roles/{role.data['id']}/users/",
        {"user_id": regular_user.id},
        kwargs={"role_id": role.data["id"]},
    )
    response = _auth_request(
        factory,
        "get",
        admin_user,
        UserPermissionCheckView,
        f"/api/rbac/users/{regular_user.id}/check/",
        {"permission": "user:create"},
        kwargs={"user_id": regular_user.id},
    )
    assert response.status_code == 200
    assert response.data["has_permission"] is True


def test_non_admin_denied(factory, regular_user):
    response = _auth_request(
        factory,
        "get",
        regular_user,
        PermissionListCreateView,
        "/api/rbac/permissions/",
    )
    assert response.status_code == 403
