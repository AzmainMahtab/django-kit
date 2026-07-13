"""RBAC DRF serializers — serialization only, no business logic."""

from rest_framework import serializers


class PermissionReadSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    resource = serializers.CharField(read_only=True)
    action = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)


class PermissionCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    resource = serializers.CharField(max_length=64)
    action = serializers.CharField(max_length=64)
    description = serializers.CharField(required=False, allow_blank=True, default="")


class RoleReadSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)


class RoleCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=64)
    description = serializers.CharField(required=False, allow_blank=True, default="")


class RolePermissionAssignSerializer(serializers.Serializer):
    permission_id = serializers.IntegerField(min_value=1)


class RoleUserAssignSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)


class UserPermissionCheckSerializer(serializers.Serializer):
    permission = serializers.CharField(max_length=128)
