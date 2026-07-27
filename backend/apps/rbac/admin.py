"""Django admin configuration for rbac."""

from django.contrib import admin
from django.db.models import Count

from backend.apps.rbac.domain.models import Permission, Role, RolePermission, UserRole


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 0
    autocomplete_fields = ("permission",)
    readonly_fields = ("assigned_at",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "resource", "action", "created_at")
    list_filter = ("resource", "action")
    search_fields = ("name", "resource", "action")
    readonly_fields = ("created_at",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "permission_count", "created_at")
    search_fields = ("name",)
    readonly_fields = ("created_at",)
    inlines = (RolePermissionInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_permission_count=Count("permissions"))

    @admin.display(description="Permissions", ordering="_permission_count")
    def permission_count(self, obj):
        return obj._permission_count


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """Standalone grant audit — who attached which permission to which role."""

    list_display = ("role", "permission", "assigned_by_id", "assigned_at")
    list_filter = ("role",)
    search_fields = ("role__name", "permission__name")
    autocomplete_fields = ("role", "permission")
    readonly_fields = ("assigned_at",)
    list_select_related = ("role", "permission")


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user_id", "role", "assigned_by_id", "assigned_at")
    list_filter = ("role",)
    search_fields = ("=user_id", "role__name")
    autocomplete_fields = ("role",)
    readonly_fields = ("assigned_at",)
    list_select_related = ("role",)
