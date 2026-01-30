import json
from typing import Any

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from pydantic import ValidationError

from application.dto.auth_dto import LoginInput, RegisterInput
from application.services.auth_service import AuthService
from domain.exceptions import AuthenticationError, EntityNotFoundError
from interface.api.dependencies import get_auth_service


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(View):
    """
    Handle user login.
    """

    def post(self, request: HttpRequest) -> JsonResponse:
        """Handle login request."""
        try:
            # Parse request body
            data = json.loads(request.body)

            # Validate input using Pydantic DTO
            login_input = LoginInput(**data)

            # Get service and execute use case
            auth_service = get_auth_service()
            output, tokens = auth_service.login(login_input)

            # Build response
            response = JsonResponse(
                {
                    "user_id": str(output.user_id),
                    "email": output.email,
                    "access_expires_in": output.access_expires_in,
                    "refresh_expires_in": output.refresh_expires_in,
                }
            )

            # Set HttpOnly cookies
            self._set_auth_cookies(response, tokens, login_input.remember_me)

            return response

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)
        except ValidationError as e:
            return JsonResponse({"error": "Validation error", "details": e.errors()}, status=400)
        except AuthenticationError as e:
            return JsonResponse({"error": str(e), "code": e.code}, status=401)

    def _set_auth_cookies(self, response: JsonResponse, tokens: Any, remember: bool) -> None:
        """Set secure HttpOnly cookies for tokens."""
        response.set_cookie(
            key=settings.JWT_ACCESS_COOKIE_NAME,
            value=tokens.access_token,
            max_age=tokens.access_expires_in,
            httponly=settings.JWT_COOKIE_HTTPONLY,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            path="/",
        )

        refresh_max_age = tokens.refresh_expires_in if remember else None
        response.set_cookie(
            key=settings.JWT_REFRESH_COOKIE_NAME,
            value=tokens.refresh_token,
            max_age=refresh_max_age,
            httponly=settings.JWT_COOKIE_HTTPONLY,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            path="/api/auth/",  # Only sent to auth endpoints
        )


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(View):
    """
    Handle user logout.
    """

    def post(self, request: HttpRequest) -> JsonResponse:
        """Handle logout request."""
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)

        if refresh_token:
            auth_service = get_auth_service()
            auth_service.logout(refresh_token)

        response = JsonResponse({"message": "Logged out successfully"})

        response.delete_cookie(
            key=settings.JWT_ACCESS_COOKIE_NAME,
            path="/",
        )
        response.delete_cookie(
            key=settings.JWT_REFRESH_COOKIE_NAME,
            path="/api/auth/",
        )

        return response


@method_decorator(csrf_exempt, name="dispatch")
class RefreshView(View):
    """
    Refresh access token.
    """

    def post(self, request: HttpRequest) -> JsonResponse:
        """Handle token refresh request."""
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)

        if not refresh_token:
            return JsonResponse(
                {"error": "No refresh token", "code": "NO_REFRESH_TOKEN"}, status=401
            )

        try:
            auth_service = get_auth_service()
            output, tokens = auth_service.refresh(refresh_token)

            response = JsonResponse(
                {
                    "access_expires_in": output.access_expires_in,
                }
            )

            response.set_cookie(
                key=settings.JWT_ACCESS_COOKIE_NAME,
                value=tokens.access_token,
                max_age=tokens.access_expires_in,
                httponly=settings.JWT_COOKIE_HTTPONLY,
                secure=settings.JWT_COOKIE_SECURE,
                samesite=settings.JWT_COOKIE_SAMESITE,
                path="/",
            )

            response.set_cookie(
                key=settings.JWT_REFRESH_COOKIE_NAME,
                value=tokens.refresh_token,
                max_age=tokens.refresh_expires_in,
                httponly=settings.JWT_COOKIE_HTTPONLY,
                secure=settings.JWT_COOKIE_SECURE,
                samesite=settings.JWT_COOKIE_SAMESITE,
                path="/api/auth/",
            )

            return response

        except AuthenticationError as e:
            response = JsonResponse({"error": str(e), "code": e.code}, status=401)
            response.delete_cookie(settings.JWT_ACCESS_COOKIE_NAME, path="/")
            response.delete_cookie(settings.JWT_REFRESH_COOKIE_NAME, path="/api/auth/")
            return response


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(View):
    """
    Handle user registration.
    """

    def post(self, request: HttpRequest) -> JsonResponse:
        """Handle registration request."""
        try:
            data = json.loads(request.body)
            register_input = RegisterInput(**data)

            auth_service = get_auth_service()
            output = auth_service.register(register_input)

            return JsonResponse(
                {
                    "user_id": str(output.user_id),
                    "email": output.email,
                    "created_at": output.created_at.isoformat(),
                },
                status=201,
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)
        except ValidationError as e:
            return JsonResponse({"error": "Validation error", "details": e.errors()}, status=400)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=409)


class MeView(View):
    """
    Get current user info.
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        """Get current user."""
        try:
            user_id = request.user_id

            auth_service = get_auth_service()
            user = auth_service.get_current_user(user_id)

            return JsonResponse(
                {
                    "id": str(user.id),
                    "email": str(user.email),
                    "is_active": user.is_active,
                    "is_staff": user.is_staff,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                }
            )

        except EntityNotFoundError:
            return JsonResponse({"error": "User not found"}, status=404)
        except AttributeError:
            return JsonResponse({"error": "Not authenticated"}, status=401)
