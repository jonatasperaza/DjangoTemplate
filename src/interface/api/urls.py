"""
API URL Configuration.

This is the main URL router for the API.
"""

from django.urls import path

from interface.api.views.auth_views import (
    LoginView,
    LogoutView,
    RefreshView,
    RegisterView,
    MeView,
)
from interface.api.views.health_views import HealthView

urlpatterns = [
    # Health check
    path("api/health", HealthView.as_view(), name="health"),
    # Authentication
    path("api/auth/login", LoginView.as_view(), name="login"),
    path("api/auth/logout", LogoutView.as_view(), name="logout"),
    path("api/auth/refresh", RefreshView.as_view(), name="refresh"),
    path("api/auth/register", RegisterView.as_view(), name="register"),
    path("api/auth/me", MeView.as_view(), name="me"),
]
