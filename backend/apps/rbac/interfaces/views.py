"""RBAC DRF views — thin views that delegate to use cases."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.rbac.interfaces.serializers import (
    PermissionCreateSerializer,
    PermissionReadSerializer,
    RoleCreateSerializer,
    RolePermissionAssignSerializer,
    RoleReadSerializer,
    RoleUserAssignSerializer,
    UserPermissionCheckSerializer,
)
from backend.shared.use_case_registry import registry


class IsRbacAdmin:
    """Allows access to staff or any user holding an rbac:* permission."""

    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        rbac = registry.get("rbac")
        permissions = rbac.queries.get_user_permissions.execute(user_id=request.user.id)
        return any(p["name"].startswith("rbac:") for p in permissions)


class _RbacPermission(IsAuthenticated):
    """Combines authentication with RBAC admin access."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return IsRbacAdmin().has_permission(request, view)


class PermissionListCreateView(APIView):
    permission_classes = [_RbacPermission]

    @extend_schema(
        tags=["RBAC"],
        summary="List permissions",
        description="Returns all RBAC permissions.",
        responses={200: PermissionReadSerializer(many=True)},
    )
    def get(self, request):
        rbac = registry.get("rbac")
        permissions = rbac.queries.list_permissions.execute()
        return Response(PermissionReadSerializer(permissions, many=True).data)

    @extend_schema(
        tags=["RBAC"],
        summary="Create permission",
        description="Creates a new RBAC permission.",
        request=PermissionCreateSerializer,
        responses={201: PermissionReadSerializer},
    )
    def post(self, request):
        serializer = PermissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rbac = registry.get("rbac")
        permission = rbac.commands.create_permission.execute(**serializer.validated_data)
        return Response(
            PermissionReadSerializer(permission).data,
            status=status.HTTP_201_CREATED,
        )


class RoleListCreateView(APIView):
    permission_classes = [_RbacPermission]

    @extend_schema(
        tags=["RBAC"],
        summary="List roles",
        description="Returns all RBAC roles.",
        responses={200: RoleReadSerializer(many=True)},
    )
    def get(self, request):
        rbac = registry.get("rbac")
        roles = rbac.queries.list_roles.execute()
        return Response(RoleReadSerializer(roles, many=True).data)

    @extend_schema(
        tags=["RBAC"],
        summary="Create role",
        description="Creates a new RBAC role.",
        request=RoleCreateSerializer,
        responses={201: RoleReadSerializer},
    )
    def post(self, request):
        serializer = RoleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rbac = registry.get("rbac")
        role = rbac.commands.create_role.execute(**serializer.validated_data)
        return Response(
            RoleReadSerializer(role).data,
            status=status.HTTP_201_CREATED,
        )


class RoleDetailView(APIView):
    permission_classes = [_RbacPermission]

    @extend_schema(
        tags=["RBAC"],
        summary="Get role",
        description="Returns a single RBAC role by id.",
        responses={200: RoleReadSerializer, 404: None},
    )
    def get(self, request, role_id: int):
        rbac = registry.get("rbac")
        role = rbac.queries.get_role.execute(role_id=role_id)
        return Response(RoleReadSerializer(role).data)


class RolePermissionAssignView(APIView):
    permission_classes = [_RbacPermission]

    @extend_schema(
        tags=["RBAC"],
        summary="Assign permission to role",
        description="Assigns a permission to the specified role.",
        request=RolePermissionAssignSerializer,
        responses={200: None, 404: None},
    )
    def post(self, request, role_id: int):
        serializer = RolePermissionAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rbac = registry.get("rbac")
        rbac.commands.assign_permission_to_role.execute(
            role_id=role_id,
            permission_id=serializer.validated_data["permission_id"],
            assigned_by_id=request.user.id,
        )
        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        tags=["RBAC"],
        summary="Revoke permission from role",
        description="Removes a permission from the specified role.",
        request=RolePermissionAssignSerializer,
        responses={200: None, 404: None},
    )
    def delete(self, request, role_id: int):
        serializer = RolePermissionAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rbac = registry.get("rbac")
        rbac.commands.revoke_permission_from_role.execute(
            role_id=role_id,
            permission_id=serializer.validated_data["permission_id"],
        )
        return Response(status=status.HTTP_200_OK)


class RoleUserAssignView(APIView):
    permission_classes = [_RbacPermission]

    @extend_schema(
        tags=["RBAC"],
        summary="Assign role to user",
        description="Assigns the specified role to a user.",
        request=RoleUserAssignSerializer,
        responses={200: None, 404: None},
    )
    def post(self, request, role_id: int):
        serializer = RoleUserAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rbac = registry.get("rbac")
        rbac.commands.assign_role_to_user.execute(
            user_id=serializer.validated_data["user_id"],
            role_id=role_id,
            assigned_by_id=request.user.id,
        )
        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        tags=["RBAC"],
        summary="Revoke role from user",
        description="Removes the specified role from a user.",
        request=RoleUserAssignSerializer,
        responses={200: None, 404: None},
    )
    def delete(self, request, role_id: int):
        serializer = RoleUserAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rbac = registry.get("rbac")
        rbac.commands.revoke_role_from_user.execute(
            user_id=serializer.validated_data["user_id"],
            role_id=role_id,
        )
        return Response(status=status.HTTP_200_OK)


class UserPermissionListView(APIView):
    permission_classes = [_RbacPermission]

    @extend_schema(
        tags=["RBAC"],
        summary="List user permissions",
        description="Returns effective permissions for a user.",
        responses={200: PermissionReadSerializer(many=True), 404: None},
    )
    def get(self, request, user_id: int):
        rbac = registry.get("rbac")
        permissions = rbac.queries.get_user_permissions.execute(user_id=user_id)
        return Response(PermissionReadSerializer(permissions, many=True).data)


class UserRoleListView(APIView):
    permission_classes = [_RbacPermission]

    @extend_schema(
        tags=["RBAC"],
        summary="List user roles",
        description="Returns roles assigned to a user.",
        responses={200: RoleReadSerializer(many=True), 404: None},
    )
    def get(self, request, user_id: int):
        rbac = registry.get("rbac")
        roles = rbac.queries.get_user_roles.execute(user_id=user_id)
        return Response(RoleReadSerializer(roles, many=True).data)


class UserPermissionCheckView(APIView):
    permission_classes = [_RbacPermission]

    @extend_schema(
        tags=["RBAC"],
        summary="Check user permission",
        description="Checks whether a user has a specific permission.",
        request=UserPermissionCheckSerializer,
        responses={200: None, 404: None},
    )
    def get(self, request, user_id: int):
        serializer = UserPermissionCheckSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        rbac = registry.get("rbac")
        result = rbac.queries.check_user_permission.execute(
            user_id=user_id,
            permission=serializer.validated_data["permission"],
        )
        return Response(result)
