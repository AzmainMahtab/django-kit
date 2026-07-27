"""Owner DRF views — thin views that delegate to use cases."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.owner.domain.exceptions import OwnerAlreadyExistsError, OwnerNotFoundError
from backend.apps.owner.interfaces.serializers import CreateOwnerSerializer, OwnerReadSerializer
from backend.core.container import get_container
from backend.shared.pagination import CustomPagination
from backend.shared.permissions import rbac_permission

OwnerCreatePermission = rbac_permission("owner:create")
OwnerReadPermission = rbac_permission("owner:read")


class OwnerListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [OwnerCreatePermission()]
        return [OwnerReadPermission()]

    @extend_schema(
        tags=["Owner"],
        summary="List owners",
        description="Returns a paginated list of owners.",
        responses={200: OwnerReadSerializer(many=True)},
    )
    def get(self, request):
        owners = get_container().owner.list_owners()
        paginator = CustomPagination()
        page = paginator.paginate_queryset(owners, request)
        return paginator.get_paginated_response(OwnerReadSerializer(page, many=True).data)

    @extend_schema(
        tags=["Owner"],
        summary="Create owner",
        description="Creates a new owner profile linked to a user.",
        request=CreateOwnerSerializer,
        responses={201: OwnerReadSerializer, 409: None},
    )
    def post(self, request):
        serializer = CreateOwnerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            owner = get_container().owner.create_owner(**serializer.validated_data)
        except OwnerAlreadyExistsError as exc:
            return Response(
                {"detail": str(exc), "code": exc.default_code},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(OwnerReadSerializer(owner).data, status=status.HTTP_201_CREATED)


class OwnerDetailView(APIView):
    permission_classes = (OwnerReadPermission,)

    @extend_schema(
        tags=["Owner"],
        summary="Get owner by UUID",
        description="Returns a single owner by UUID.",
        responses={200: OwnerReadSerializer, 404: None},
    )
    def get(self, request, owner_uuid: str):
        try:
            owner = get_container().owner.get_owner_by_uuid(uuid=owner_uuid)
        except OwnerNotFoundError as exc:
            return Response(
                {"detail": str(exc), "code": exc.default_code},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(OwnerReadSerializer(owner).data)


class OwnerByUserView(APIView):
    permission_classes = (OwnerReadPermission,)

    @extend_schema(
        tags=["Owner"],
        summary="Get owner by user ID",
        description="Returns the owner profile associated with a user.",
        responses={200: OwnerReadSerializer, 404: None},
    )
    def get(self, request, user_id: int):
        try:
            owner = get_container().owner.get_owner_by_user_id(user_id=user_id)
        except OwnerNotFoundError as exc:
            return Response(
                {"detail": str(exc), "code": exc.default_code},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(OwnerReadSerializer(owner).data)
