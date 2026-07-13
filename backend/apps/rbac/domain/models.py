"""RBAC domain models."""

from django.conf import settings
from django.db import models


class Permission(models.Model):
    """A granular permission tied to a resource and action."""

    name = models.CharField(max_length=128, unique=True, db_index=True)
    description = models.TextField(blank=True, default="")
    resource = models.CharField(max_length=64, db_index=True)
    action = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rbac_permission"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Role(models.Model):
    """A named collection of permissions that can be assigned to users."""

    name = models.CharField(max_length=64, unique=True, db_index=True)
    description = models.TextField(blank=True, default="")
    permissions = models.ManyToManyField(
        Permission,
        through="RolePermission",
        related_name="roles",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rbac_role"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class RolePermission(models.Model):
    """Through model linking a Role to a Permission."""

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_role_permissions",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rbac_role_permission"
        unique_together = [("role", "permission")]


class UserRole(models.Model):
    """Through model linking a User to a Role."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_user_roles",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rbac_user_role"
        unique_together = [("user", "role")]
