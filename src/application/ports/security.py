from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import uuid


@dataclass
class TokenPair:
    """Represents a pair of access and refresh tokens."""

    access_token: str
    refresh_token: str
    access_expires_in: int  # seconds
    refresh_expires_in: int  # seconds
    token_type: str = "Bearer"


@dataclass
class TokenPayload:
    """Decoded token payload."""

    user_id: uuid.UUID
    token_type: str  # 'access' or 'refresh'
    jti: Optional[str] = None  # JWT ID for refresh token blacklisting
    exp: Optional[int] = None  # Expiration timestamp


class SecurityPort(ABC):
    """
    Abstract interface for security operations.

    This port abstracts away the specifics of password hashing
    and JWT token management from the application layer.
    """

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        """
        Hash a plain text password.

        Args:
            plain_password: The password to hash.

        Returns:
            The hashed password string.
        """
        ...

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: The password to verify.
            hashed_password: The stored hash.

        Returns:
            True if password matches, False otherwise.
        """
        ...

    @abstractmethod
    def generate_tokens(self, user_id: uuid.UUID) -> TokenPair:
        """
        Generate access and refresh tokens for a user.

        Args:
            user_id: The user's unique identifier.

        Returns:
            A TokenPair with access and refresh tokens.
        """
        ...

    @abstractmethod
    def decode_token(self, token: str) -> TokenPayload:
        """
        Decode and validate a JWT token.

        Args:
            token: The JWT token string.

        Returns:
            The decoded TokenPayload.

        Raises:
            TokenExpiredError: If the token has expired.
            TokenInvalidError: If the token is invalid.
        """
        ...

    @abstractmethod
    def revoke_token(self, jti: str) -> None:
        """
        Revoke a refresh token by its JTI.

        This adds the token to a blacklist, preventing its reuse.

        Args:
            jti: The JWT ID of the token to revoke.
        """
        ...

    @abstractmethod
    def is_token_revoked(self, jti: str) -> bool:
        """
        Check if a token has been revoked.

        Args:
            jti: The JWT ID to check.

        Returns:
            True if revoked, False otherwise.
        """
        ...


class TokenExpiredError(Exception):
    """Raised when a token has expired."""

    pass


class TokenInvalidError(Exception):
    """Raised when a token is invalid."""

    pass
