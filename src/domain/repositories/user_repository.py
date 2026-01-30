from abc import ABC, abstractmethod
from typing import Optional
import uuid

from domain.entities.user import User


class UserRepository(ABC):
    """
    Abstract repository interface for User entity.

    This is a PORT in hexagonal architecture terms. Implementations
    (ADAPTERS) live in the infrastructure layer.
    """

    @abstractmethod
    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Retrieve a user by their unique identifier.

        Args:
            user_id: The user's UUID.

        Returns:
            The User entity if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.

        Args:
            email: The user's email address.

        Returns:
            The User entity if found, None otherwise.
        """
        ...

    @abstractmethod
    def save(self, user: User) -> User:
        """
        Persist a user entity.

        If the user already exists (by ID), update it.
        If it's new, create it.

        Args:
            user: The User entity to persist.

        Returns:
            The persisted User entity.
        """
        ...

    @abstractmethod
    def delete(self, user_id: uuid.UUID) -> bool:
        """
        Delete a user by their ID.

        Args:
            user_id: The user's UUID.

        Returns:
            True if deleted, False if not found.
        """
        ...

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """
        Check if a user with the given email exists.

        Args:
            email: The email to check.

        Returns:
            True if exists, False otherwise.
        """
        ...

    @abstractmethod
    def list_active(self, limit: int = 100, offset: int = 0) -> list[User]:
        """
        List active users with pagination.

        Args:
            limit: Maximum number of users to return.
            offset: Number of users to skip.

        Returns:
            List of active User entities.
        """
        ...

    @abstractmethod
    def count_active(self) -> int:
        """
        Count total number of active users.

        Returns:
            Number of active users.
        """
        ...
