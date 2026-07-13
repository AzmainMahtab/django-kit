"""URL configuration for core project."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("backend.apps.identity.interfaces.urls")),
    path("api/otp/", include("backend.apps.otp.interfaces.urls")),
    path("api/rbac/", include("backend.apps.rbac.interfaces.urls")),
    path("api/", include("backend.apps.owner.interfaces.urls")),
    path("api/", include("backend.apps.car.interfaces.urls")),
    path("api/", include("backend.apps.ordering.interfaces.urls")),
    path("api/", include("backend.apps.notification.interfaces.urls")),
]

if settings.DEBUG:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )

    urlpatterns += [
        path("api/", SpectacularSwaggerView.as_view(url_name="schema")),
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema")),
    ]
