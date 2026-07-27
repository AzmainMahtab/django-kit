"""Ordering DRF views — thin views that delegate to use cases."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.ordering.interfaces.serializers import (
    JobStatusTransitionSerializer,
    OrderCreateSerializer,
    OrderSerializer,
)
from backend.core.container import get_container


class OrderListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Ordering"],
        summary="List orders",
        description="Returns a list of orders.",
        responses={200: OrderSerializer(many=True)},
    )
    def get(self, request):
        ordering = get_container().ordering
        result = ordering.queries.list_orders.execute()
        return Response(OrderSerializer(result, many=True).data)

    @extend_schema(
        tags=["Ordering"],
        summary="Create an order",
        description="Create a new order with one or more production jobs.",
        request=OrderCreateSerializer,
        responses={201: OrderSerializer},
    )
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ordering = get_container().ordering
        result = ordering.commands.create_order.execute(**serializer.validated_data)
        return Response(OrderSerializer(result).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Ordering"],
        summary="Get an order",
        description="Returns a single order by id.",
        responses={200: OrderSerializer, 404: None},
    )
    def get(self, request, order_id: int):
        ordering = get_container().ordering
        result = ordering.queries.get_order.execute(order_id=order_id)
        return Response(OrderSerializer(result).data)


class JobStatusTransitionView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Ordering"],
        summary="Transition job status",
        description="Transition a job through the production state machine.",
        request=JobStatusTransitionSerializer,
        responses={200: OrderSerializer, 400: None, 404: None},
    )
    def post(self, request, job_id: int):
        serializer = JobStatusTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ordering = get_container().ordering
        result = ordering.commands.transition_job_status.execute(
            job_id=job_id,
            user_id=request.user.id,
            **serializer.validated_data,
        )
        return Response(OrderSerializer(result).data)
