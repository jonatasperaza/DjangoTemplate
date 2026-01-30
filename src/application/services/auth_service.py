from dataclasses import dataclass
import uuid

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from domain.exceptions import AuthenticationError, EntityNotFoundError
from application.ports.security import (
    SecurityPort,
    TokenPair,
    TokenExpiredError,
    TokenInvalidError,
)
from application.ports.messaging import MessagingPort, DomainEvent
from application.dto.auth_dto import (
    LoginInput,
    LoginOutput,
    RefreshOutput,
    RegisterInput,
    RegisterOutput,
)


@dataclass
class AuthService:
    """
    Application service for authentication operations.

    This service implements authentication use cases by coordinating
    between domain entities and infrastructure ports.
    """

    user_repo: UserRepository
    security_port: SecurityPort
    messaging_port: MessagingPort

    def login(self, dto: LoginInput) -> tuple[LoginOutput, TokenPair]:
        """
        Authenticate a user and generate tokens.

        Args:
            dto: Login input with email and password.

        Returns:
            Tuple of LoginOutput and TokenPair.

        Raises:
            AuthenticationError: If credentials are invalid.
        """
        # Find user by email
        user = self.user_repo.get_by_email(dto.email)

        if not user:
            # Don't reveal whether email exists
            raise AuthenticationError("Invalid email or password.")

        # Verify password
        if not user.password_hash:
            raise AuthenticationError("Invalid email or password.")

        if not self.security_port.verify_password(dto.password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")

        # Check if user is active
        if not user.is_active:
            raise AuthenticationError("Account is deactivated.")

        # Record login
        user.record_login()
        self.user_repo.save(user)

        # Generate tokens
        tokens = self.security_port.generate_tokens(user.id)

        # Publish login event
        self.messaging_port.publish_event(
            DomainEvent(
                event_type="user.logged_in",
                payload={"user_id": str(user.id), "email": str(user.email)},
            )
        )

        output = LoginOutput(
            user_id=user.id,
            email=str(user.email),
            access_expires_in=tokens.access_expires_in,
            refresh_expires_in=tokens.refresh_expires_in,
        )

        return output, tokens

    def logout(self, refresh_token: str) -> None:
        """
        Logout user by revoking their refresh token.

        Args:
            refresh_token: The refresh token to revoke.
        """
        try:
            payload = self.security_port.decode_token(refresh_token)
            if payload.jti:
                self.security_port.revoke_token(payload.jti)
        except (TokenExpiredError, TokenInvalidError):
            # Token already invalid, nothing to revoke
            pass

    def refresh(self, refresh_token: str) -> tuple[RefreshOutput, TokenPair]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: The refresh token.

        Returns:
            Tuple of RefreshOutput and new TokenPair.

        Raises:
            AuthenticationError: If refresh token is invalid or revoked.
        """
        try:
            payload = self.security_port.decode_token(refresh_token)
        except TokenExpiredError:
            raise AuthenticationError("Refresh token expired. Please login again.")
        except TokenInvalidError:
            raise AuthenticationError("Invalid refresh token.")

        # Check if token is revoked
        if payload.jti and self.security_port.is_token_revoked(payload.jti):
            raise AuthenticationError("Token has been revoked.")

        # Verify user still exists and is active
        user = self.user_repo.get_by_id(payload.user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive.")

        # Revoke old refresh token
        if payload.jti:
            self.security_port.revoke_token(payload.jti)

        # Generate new tokens
        tokens = self.security_port.generate_tokens(user.id)

        output = RefreshOutput(access_expires_in=tokens.access_expires_in)

        return output, tokens

    def register(self, dto: RegisterInput) -> RegisterOutput:
        """
        Register a new user.

        Args:
            dto: Registration input with email and password.

        Returns:
            RegisterOutput with user data.

        Raises:
            ValueError: If email already exists.
        """
        # Check if email already exists
        if self.user_repo.exists_by_email(dto.email):
            raise ValueError("Email already registered.")

        # Hash password
        password_hash = self.security_port.hash_password(dto.password)

        # Create user entity
        user = User(
            email=dto.email,
            password_hash=password_hash,
        )

        # Persist user
        saved_user = self.user_repo.save(user)

        # Publish registration event
        self.messaging_port.publish_event(
            DomainEvent(
                event_type="user.registered",
                payload={"user_id": str(saved_user.id), "email": str(saved_user.email)},
            )
        )

        return RegisterOutput(
            user_id=saved_user.id,
            email=str(saved_user.email),
            created_at=saved_user.created_at,
        )

    def get_current_user(self, user_id: uuid.UUID) -> User:
        """
        Get current user by ID.

        Args:
            user_id: The user's UUID.

        Returns:
            The User entity.

        Raises:
            EntityNotFoundError: If user not found.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", str(user_id))
        return user
