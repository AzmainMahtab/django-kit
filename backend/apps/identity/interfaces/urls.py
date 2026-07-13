"""Identity URL configuration."""

from django.urls import path

from backend.apps.identity.interfaces.views import (
    LoginView,
    LogoutView,
    ProfileView,
    RefreshView,
    UserDetailView,
    UserListCreateView,
)

urlpatterns = [
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/<int:user_id>/", UserDetailView.as_view(), name="user-detail"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", RefreshView.as_view(), name="refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/profile/", ProfileView.as_view(), name="profile"),
]
