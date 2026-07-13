"""Owner URL configuration."""

from django.urls import path

from backend.apps.owner.interfaces.views import (
    OwnerByUserView,
    OwnerDetailView,
    OwnerListCreateView,
)

urlpatterns = [
    path("owners/", OwnerListCreateView.as_view(), name="owner-list-create"),
    path("owners/<uuid:owner_uuid>/", OwnerDetailView.as_view(), name="owner-detail"),
    path("owners/by-user/<int:user_id>/", OwnerByUserView.as_view(), name="owner-by-user"),
]
