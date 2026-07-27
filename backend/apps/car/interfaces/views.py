"""Car DRF views — thin views that delegate to use cases."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.car.domain.exceptions import CarAlreadyExistsError, CarNotFoundError
from backend.apps.car.interfaces.serializers import CarReadSerializer, CreateCarSerializer
from backend.core.container import get_container
from backend.shared.pagination import CustomPagination
from backend.shared.permissions import rbac_permission

CarCreatePermission = rbac_permission("car:create")
CarReadPermission = rbac_permission("car:read")


class CarListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CarCreatePermission()]
        return [CarReadPermission()]

    @extend_schema(
        tags=["Car"],
        summary="List cars",
        description="Returns a paginated list of all cars.",
        responses={200: CarReadSerializer(many=True)},
    )
    def get(self, request):
        cars = get_container().car.list_cars()
        paginator = CustomPagination()
        page = paginator.paginate_queryset(cars, request)
        return paginator.get_paginated_response(CarReadSerializer(page, many=True).data)

    @extend_schema(
        tags=["Car"],
        summary="Create car",
        description="Creates a new car for an owner.",
        request=CreateCarSerializer,
        responses={201: CarReadSerializer, 404: None, 409: None},
    )
    def post(self, request):
        serializer = CreateCarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            car = get_container().car.create_car(**serializer.validated_data)
        except CarAlreadyExistsError as exc:
            return Response(
                {"detail": str(exc), "code": exc.default_code},
                status=status.HTTP_409_CONFLICT,
            )
        except CarNotFoundError as exc:
            return Response(
                {"detail": str(exc), "code": exc.default_code},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(CarReadSerializer(car).data, status=status.HTTP_201_CREATED)


class CarDetailView(APIView):
    permission_classes = (CarReadPermission,)

    @extend_schema(
        tags=["Car"],
        summary="Get car by UUID",
        description="Returns a single car by UUID.",
        responses={200: CarReadSerializer, 404: None},
    )
    def get(self, request, car_uuid: str):
        try:
            car = get_container().car.get_car_by_uuid(uuid=car_uuid)
        except CarNotFoundError as exc:
            return Response(
                {"detail": str(exc), "code": exc.default_code},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(CarReadSerializer(car).data)


class CarByOwnerView(APIView):
    permission_classes = (CarReadPermission,)

    @extend_schema(
        tags=["Car"],
        summary="List cars by owner",
        description="Returns a paginated list of cars for an owner.",
        responses={200: CarReadSerializer(many=True)},
    )
    def get(self, request, owner_id: int):
        cars = get_container().car.list_cars_by_owner(owner_id=owner_id)
        paginator = CustomPagination()
        page = paginator.paginate_queryset(cars, request)
        return paginator.get_paginated_response(CarReadSerializer(page, many=True).data)
