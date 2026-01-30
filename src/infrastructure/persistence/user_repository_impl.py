from typing import Optional
import uuid

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from infrastructure.django.models.user_model import UserModel
from infrastructure.persistence.mappers.user_mapper import UserMapper


class DjangoUserRepository(UserRepository):
    """
    Repository implementation using Django ORM.

    This adapter translates between domain operations and Django ORM calls.
    It uses the UserMapper to convert between UserModel and User entity.
    """

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Retrieve a user by ID.

        Args:
            user_id: The user's UUID.

        Returns:
            User entity if found, None otherwise.
        """
        try:
            model = UserModel.objects.get(id=user_id)
            return UserMapper.to_entity(model)
        except UserModel.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email.

        Args:
            email: The user's email address.

        Returns:
            User entity if found, None otherwise.
        """
        try:
            model = UserModel.objects.get(email__iexact=email)
            return UserMapper.to_entity(model)
        except UserModel.DoesNotExist:
            return None

    def save(self, user: User) -> User:
        """
        Persist a user entity.

        Handles both create and update operations.

        Args:
            user: The User entity to persist.

        Returns:
            The persisted User entity.
        """
        # Check if user exists
        try:
            existing_model = UserModel.objects.get(id=user.id)
            # Update existing
            model = UserMapper.update_model(existing_model, user)
        except UserModel.DoesNotExist:
            # Create new
            model = UserMapper.to_model(user)

        model.save()
        return UserMapper.to_entity(model)

    def delete(self, user_id: uuid.UUID) -> bool:
        """
        Delete a user by ID.

        Args:
            user_id: The user's UUID.

        Returns:
            True if deleted, False if not found.
        """
        try:
            model = UserModel.objects.get(id=user_id)
            model.delete()
            return True
        except UserModel.DoesNotExist:
            return False

    def exists_by_email(self, email: str) -> bool:
        """
        Check if a user with email exists.

        Args:
            email: The email to check.

        Returns:
            True if exists, False otherwise.
        """
        return UserModel.objects.filter(email__iexact=email).exists()

    def list_active(self, limit: int = 100, offset: int = 0) -> list[User]:
        """
        List active users with pagination.

        Args:
            limit: Maximum number of users to return.
            offset: Number of users to skip.

        Returns:
            List of active User entities.
        """
        models = UserModel.objects.filter(is_active=True).order_by("-date_joined")[
            offset : offset + limit
        ]
        return [UserMapper.to_entity(m) for m in models]

    def count_active(self) -> int:
        """
        Count active users.

        Returns:
            Number of active users.
        """
        return UserModel.objects.filter(is_active=True).count()
