from typing import Callable
import uuid

from django.conf import settings
from django.http import HttpRequest, JsonResponse

from infrastructure.security.cookie_auth import CookieJWTAdapter
from application.ports.security import TokenExpiredError, TokenInvalidError


class JWTAuthMiddleware:
    """
    Middleware that validates JWT tokens from cookies.

    Public endpoints are defined in PUBLIC_PATHS and bypass authentication.
    For authenticated requests, user_id is injected into request.
    """

    # Paths that don't require authentication
    PUBLIC_PATHS = [
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/refresh",
        "/api/health",
        "/api/docs",
    ]

    # Prefixes that are always public
    PUBLIC_PREFIXES = [
        "/static/",
        "/media/",
    ]

    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        self.security = CookieJWTAdapter()

    def __call__(self, request: HttpRequest):
        """Process the request."""
        # Skip auth for public paths
        if self._is_public_path(request.path):
            return self.get_response(request)

        # Get access token from cookie
        access_token = request.COOKIES.get(settings.JWT_ACCESS_COOKIE_NAME, None)

        if not access_token:
            return JsonResponse(
                {"error": "Authentication required", "code": "NO_TOKEN"}, status=401
            )

        try:
            # Decode and validate token
            payload = self.security.decode_token(access_token)

            # Check token type
            if payload.token_type != "access":
                return JsonResponse(
                    {"error": "Invalid token type", "code": "INVALID_TOKEN_TYPE"}, status=401
                )

            # Inject user_id into request
            request.user_id = payload.user_id
            request.is_authenticated = True

        except TokenExpiredError:
            return JsonResponse({"error": "Token expired", "code": "TOKEN_EXPIRED"}, status=401)
        except TokenInvalidError:
            return JsonResponse({"error": "Invalid token", "code": "INVALID_TOKEN"}, status=401)

        return self.get_response(request)

    def _is_public_path(self, path: str) -> bool:
        """Check if path is public (no auth required)."""
        # Check exact matches
        if path in self.PUBLIC_PATHS:
            return True

        # Check without trailing slash
        if path.rstrip("/") in self.PUBLIC_PATHS:
            return True

        # Check prefixes
        for prefix in self.PUBLIC_PREFIXES:
            if path.startswith(prefix):
                return True

        return False


def get_current_user_id(request: HttpRequest) -> uuid.UUID:
    """
    Helper to get the current user ID from request.

    Args:
        request: Django HttpRequest.

    Returns:
        User UUID.

    Raises:
        AttributeError: If user is not authenticated.
    """
    if not hasattr(request, "user_id"):
        raise AttributeError("User not authenticated")
    return request.user_id
