from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

import jwt
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache

from application.ports.security import (
    SecurityPort,
    TokenPair,
    TokenPayload,
    TokenExpiredError,
    TokenInvalidError,
)


class CookieJWTAdapter(SecurityPort):
    """
    Security adapter using JWT tokens in HttpOnly cookies.

    This implementation:
    - Uses Django's password hashers for password hashing
    - Generates JWT tokens for authentication
    - Uses Redis (via Django cache) for token blacklist
    """

    def __init__(self) -> None:
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_lifetime = timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME)
        self.refresh_token_lifetime = timedelta(seconds=settings.JWT_REFRESH_TOKEN_LIFETIME)
        self.blacklist_prefix = "jwt_blacklist:"

    def hash_password(self, plain_password: str) -> str:
        """
        Hash a password using Django's password hashers.

        Args:
            plain_password: The plain text password.

        Returns:
            The hashed password.
        """
        return make_password(plain_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: The password to verify.
            hashed_password: The stored hash.

        Returns:
            True if password matches.
        """
        return check_password(plain_password, hashed_password)

    def generate_tokens(self, user_id: uuid.UUID) -> TokenPair:
        """
        Generate access and refresh token pair.

        Args:
            user_id: The user's UUID.

        Returns:
            TokenPair with access and refresh tokens.
        """
        now = datetime.now(timezone.utc)

        # Access token payload
        access_payload = {
            "user_id": str(user_id),
            "type": "access",
            "iat": now,
            "exp": now + self.access_token_lifetime,
        }

        # Refresh token payload with JTI for blacklisting
        jti = str(uuid.uuid4())
        refresh_payload = {
            "user_id": str(user_id),
            "type": "refresh",
            "jti": jti,
            "iat": now,
            "exp": now + self.refresh_token_lifetime,
        }

        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_in=int(self.access_token_lifetime.total_seconds()),
            refresh_expires_in=int(self.refresh_token_lifetime.total_seconds()),
        )

    def decode_token(self, token: str) -> TokenPayload:
        """
        Decode and validate a JWT token.

        Args:
            token: The JWT token string.

        Returns:
            Decoded TokenPayload.

        Raises:
            TokenExpiredError: If token has expired.
            TokenInvalidError: If token is invalid.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            return TokenPayload(
                user_id=uuid.UUID(payload["user_id"]),
                token_type=payload["type"],
                jti=payload.get("jti"),
                exp=payload.get("exp"),
            )

        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise TokenInvalidError(f"Invalid token: {e}")

    def revoke_token(self, jti: str) -> None:
        """
        Revoke a token by adding its JTI to the blacklist.

        Uses Redis (via Django cache) with TTL matching refresh token lifetime.

        Args:
            jti: The JWT ID to revoke.
        """
        cache_key = f"{self.blacklist_prefix}{jti}"
        # Set with TTL equal to refresh token lifetime
        cache.set(cache_key, True, timeout=int(self.refresh_token_lifetime.total_seconds()))

    def is_token_revoked(self, jti: str) -> bool:
        """
        Check if a token JTI is in the blacklist.

        Args:
            jti: The JWT ID to check.

        Returns:
            True if revoked.
        """
        cache_key = f"{self.blacklist_prefix}{jti}"
        return cache.get(cache_key) is not None


def get_user_id_from_token(token: str) -> Optional[uuid.UUID]:
    """
    Helper function to extract user ID from a token.

    Args:
        token: The JWT token.

    Returns:
        User UUID if valid, None otherwise.
    """
    adapter = CookieJWTAdapter()
    try:
        payload = adapter.decode_token(token)
        return payload.user_id
    except (TokenExpiredError, TokenInvalidError):
        return None
