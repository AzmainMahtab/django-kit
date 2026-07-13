"""Car URL configuration."""

from django.urls import path

from backend.apps.car.interfaces.views import (
    CarByOwnerView,
    CarDetailView,
    CarListCreateView,
)

urlpatterns = [
    path("cars/", CarListCreateView.as_view(), name="car-list-create"),
    path("cars/<uuid:car_uuid>/", CarDetailView.as_view(), name="car-detail"),
    path("cars/by-owner/<int:owner_id>/", CarByOwnerView.as_view(), name="car-by-owner"),
]
