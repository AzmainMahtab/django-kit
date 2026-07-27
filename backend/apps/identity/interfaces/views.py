"""Identity DRF views — thin views that delegate to use cases."""

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.identity.interfaces.serializers import (
    LoginSerializer,
    LogoutSerializer,
    RefreshSerializer,
    TokenResponseSerializer,
    UserCreateSerializer,
    UserListQuerySerializer,
    UserReadSerializer,
    UserUpdateSerializer,
)
from backend.core.container import get_container
from backend.shared.pagination import CustomPagination


class UserListCreateView(APIView):
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(
        tags=["Identity"],
        summary="List users",
        description="Returns a paginated list of users.",
        request=UserListQuerySerializer,
        responses={200: UserReadSerializer(many=True)},
    )
    def get(self, request):
        params = UserListQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)

        filters = {}
        if params.validated_data.get("is_staff") is not None:
            filters["is_staff"] = params.validated_data["is_staff"]
        if params.validated_data.get("is_active") is not None:
            filters["is_active"] = params.validated_data["is_active"]

        identity = get_container().identity
        users = identity.queries.list_users.execute(filters=filters)

        paginator = CustomPagination()
        page = paginator.paginate_queryset(users, request)
        return paginator.get_paginated_response(UserReadSerializer(page, many=True).data)

    @extend_schema(
        tags=["Identity"],
        summary="Create a user",
        description="Registers a new user account.",
        request=UserCreateSerializer,
        responses={201: UserReadSerializer},
        examples=[
            OpenApiExample(
                "Create user",
                value={
                    "username": "jane_doe",
                    "email": "jane@example.com",
                    "password": "super-secret-123",
                    "first_name": "Jane",
                    "last_name": "Doe",
                },
            )
        ],
    )
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identity = get_container().identity
        result = identity.commands.create_user.execute(**serializer.validated_data)

        return Response(UserReadSerializer(result).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Identity"],
        summary="Get a user",
        description="Returns a single user by id.",
        responses={200: UserReadSerializer, 404: None},
    )
    def get(self, request, user_id: int):
        identity = get_container().identity
        result = identity.queries.get_user.execute(user_id=user_id)
        return Response(UserReadSerializer(result).data)

    @extend_schema(
        tags=["Identity"],
        summary="Update a user",
        description="Updates an existing user.",
        request=UserUpdateSerializer,
        responses={200: UserReadSerializer, 404: None},
    )
    def patch(self, request, user_id: int):
        serializer = UserUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        identity = get_container().identity
        result = identity.commands.update_user.execute(user_id=user_id, **serializer.validated_data)
        return Response(UserReadSerializer(result).data)

    @extend_schema(
        tags=["Identity"],
        summary="Delete a user",
        description="Deletes a user account.",
        responses={204: None, 404: None},
    )
    def delete(self, request, user_id: int):
        identity = get_container().identity
        identity.commands.delete_user.execute(user_id=user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginView(APIView):
    permission_classes = (AllowAny,)
    throttle_scope = "login"

    @extend_schema(
        tags=["Identity"],
        summary="Authenticate",
        description="Exchange email/password for a JWT token pair.",
        request=LoginSerializer,
        responses={200: TokenResponseSerializer},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identity = get_container().identity
        tokens = identity.commands.login.execute(**serializer.validated_data)
        return Response(TokenResponseSerializer(tokens).data)


class RefreshView(APIView):
    permission_classes = (AllowAny,)
    throttle_scope = "refresh"

    @extend_schema(
        tags=["Identity"],
        summary="Refresh tokens",
        description="Exchange a valid refresh token for a fresh token pair.",
        request=RefreshSerializer,
        responses={200: TokenResponseSerializer},
    )
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identity = get_container().identity
        tokens = identity.commands.refresh_token.execute(**serializer.validated_data)
        return Response(TokenResponseSerializer(tokens).data)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Identity"],
        summary="Logout",
        description="Revoke the current access and refresh tokens.",
        request=LogoutSerializer,
        responses={204: None},
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ", 1)[1]

        identity = get_container().identity
        identity.commands.logout.execute(
            refresh_token=serializer.validated_data["refresh_token"],
            access_token=access_token,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Identity"],
        summary="Get profile",
        description="Return the authenticated user's profile.",
        responses={200: UserReadSerializer},
    )
    def get(self, request):
        identity = get_container().identity
        result = identity.queries.get_profile.execute(user_id=request.user.id)
        return Response(UserReadSerializer(result).data)
