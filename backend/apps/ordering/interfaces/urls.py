"""Ordering URL configuration."""

from django.urls import path

from backend.apps.ordering.interfaces.views import (
    JobStatusTransitionView,
    OrderDetailView,
    OrderListCreateView,
)

urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:order_id>/", OrderDetailView.as_view(), name="order-detail"),
    path(
        "jobs/<int:job_id>/transition/",
        JobStatusTransitionView.as_view(),
        name="job-status-transition",
    ),
]
