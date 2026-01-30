from functools import lru_cache

from application.services.auth_service import AuthService
from application.services.user_management import UserManagementService
from infrastructure.persistence.user_repository_impl import DjangoUserRepository
from infrastructure.security.cookie_auth import CookieJWTAdapter
from infrastructure.messaging.celery_adapter import CeleryMessagingAdapter


@lru_cache(maxsize=1)
def get_user_repository() -> DjangoUserRepository:
    """Get the user repository singleton."""
    return DjangoUserRepository()


@lru_cache(maxsize=1)
def get_security_port() -> CookieJWTAdapter:
    """Get the security port singleton."""
    return CookieJWTAdapter()


@lru_cache(maxsize=1)
def get_messaging_port() -> CeleryMessagingAdapter:
    """Get the messaging port singleton."""
    return CeleryMessagingAdapter()


def get_auth_service() -> AuthService:
    """
    Factory function for AuthService.
    """

    return AuthService(
        user_repo=get_user_repository(),
        security_port=get_security_port(),
        messaging_port=get_messaging_port(),
    )


def get_user_management_service() -> UserManagementService:
    """
    Factory function for UserManagementService.
    """
    return UserManagementService(
        user_repo=get_user_repository(),
        security_port=get_security_port(),
    )
