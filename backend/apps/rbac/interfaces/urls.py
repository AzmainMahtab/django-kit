"""RBAC URL configuration."""

from django.urls import path

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

urlpatterns = [
    path("permissions/", PermissionListCreateView.as_view(), name="rbac-permission-list-create"),
    path("roles/", RoleListCreateView.as_view(), name="rbac-role-list-create"),
    path("roles/<int:role_id>/", RoleDetailView.as_view(), name="rbac-role-detail"),
    path(
        "roles/<int:role_id>/permissions/",
        RolePermissionAssignView.as_view(),
        name="rbac-role-permission-assign",
    ),
    path(
        "roles/<int:role_id>/users/",
        RoleUserAssignView.as_view(),
        name="rbac-role-user-assign",
    ),
    path(
        "users/<int:user_id>/permissions/",
        UserPermissionListView.as_view(),
        name="rbac-user-permissions",
    ),
    path(
        "users/<int:user_id>/roles/",
        UserRoleListView.as_view(),
        name="rbac-user-roles",
    ),
    path(
        "users/<int:user_id>/check/",
        UserPermissionCheckView.as_view(),
        name="rbac-user-check",
    ),
]
