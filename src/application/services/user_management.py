from dataclasses import dataclass
from math import ceil
import uuid

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from domain.exceptions import (
    EntityNotFoundError,
    DuplicateEntityError,
    AuthorizationError,
)
from application.ports.security import SecurityPort
from application.dto.user_dto import (
    UserCreateInput,
    UserUpdateInput,
    UserListInput,
    UserListOutput,
    UserOutput,
)


@dataclass
class UserManagementService:
    """
    Application service for user management operations.

    These are admin-level operations for managing users.
    """

    user_repo: UserRepository
    security_port: SecurityPort

    def create_user(self, dto: UserCreateInput, created_by: User) -> UserOutput:
        """
        Create a new user (admin operation).

        Args:
            dto: User creation input.
            created_by: The admin user creating this user.

        Returns:
            UserOutput with created user data.

        Raises:
            AuthorizationError: If creator is not staff.
            DuplicateEntityError: If email already exists.
        """
        if not created_by.is_staff:
            raise AuthorizationError("Only staff can create users.")

        if self.user_repo.exists_by_email(dto.email):
            raise DuplicateEntityError("User", "email", dto.email)

        password_hash = self.security_port.hash_password(dto.password)

        user = User(
            email=dto.email,
            password_hash=password_hash,
            is_staff=dto.is_staff,
            is_active=dto.is_active,
        )

        saved_user = self.user_repo.save(user)

        return UserOutput(
            id=saved_user.id,
            email=str(saved_user.email),
            is_active=saved_user.is_active,
            is_staff=saved_user.is_staff,
            is_superuser=saved_user.is_superuser,
            created_at=saved_user.created_at,
            updated_at=saved_user.updated_at,
            last_login=saved_user.last_login,
        )

    def get_user(self, user_id: uuid.UUID) -> UserOutput:
        """
        Get a user by ID.

        Args:
            user_id: The user's UUID.

        Returns:
            UserOutput with user data.

        Raises:
            EntityNotFoundError: If user not found.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", str(user_id))

        return UserOutput(
            id=user.id,
            email=str(user.email),
            is_active=user.is_active,
            is_staff=user.is_staff,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
        )

    def update_user(
        self,
        user_id: uuid.UUID,
        dto: UserUpdateInput,
        updated_by: User,
    ) -> UserOutput:
        """
        Update a user.

        Args:
            user_id: The user's UUID.
            dto: Update input.
            updated_by: The user performing the update.

        Returns:
            UserOutput with updated user data.

        Raises:
            EntityNotFoundError: If user not found.
            AuthorizationError: If not authorized to update.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", str(user_id))

        # Check permissions
        is_self = user.id == updated_by.id
        is_admin = updated_by.is_staff or updated_by.is_superuser

        if not is_self and not is_admin:
            raise AuthorizationError("Cannot update other users.")

        # Apply updates
        if dto.email is not None:
            if self.user_repo.exists_by_email(dto.email):
                existing = self.user_repo.get_by_email(dto.email)
                if existing and existing.id != user.id:
                    raise DuplicateEntityError("User", "email", dto.email)
            user.update_email(dto.email)

        if dto.is_active is not None and is_admin:
            if dto.is_active:
                user.activate()
            else:
                user.deactivate()

        if dto.is_staff is not None and updated_by.is_superuser:
            if dto.is_staff:
                user.promote_to_staff()
            else:
                user.demote_from_staff()

        saved_user = self.user_repo.save(user)

        return UserOutput(
            id=saved_user.id,
            email=str(saved_user.email),
            is_active=saved_user.is_active,
            is_staff=saved_user.is_staff,
            is_superuser=saved_user.is_superuser,
            created_at=saved_user.created_at,
            updated_at=saved_user.updated_at,
            last_login=saved_user.last_login,
        )

    def list_users(self, dto: UserListInput) -> UserListOutput:
        """
        List users with pagination.

        Args:
            dto: List input with pagination.

        Returns:
            UserListOutput with paginated users.
        """
        offset = (dto.page - 1) * dto.page_size

        users = self.user_repo.list_active(limit=dto.page_size, offset=offset)
        total = self.user_repo.count_active()

        user_outputs = [
            UserOutput(
                id=u.id,
                email=str(u.email),
                is_active=u.is_active,
                is_staff=u.is_staff,
                is_superuser=u.is_superuser,
                created_at=u.created_at,
                updated_at=u.updated_at,
                last_login=u.last_login,
            )
            for u in users
        ]

        return UserListOutput(
            users=user_outputs,
            total=total,
            page=dto.page,
            page_size=dto.page_size,
            total_pages=ceil(total / dto.page_size) if total > 0 else 1,
        )

    def delete_user(self, user_id: uuid.UUID, deleted_by: User) -> bool:
        """
        Delete a user.

        Args:
            user_id: The user's UUID.
            deleted_by: The user performing the deletion.

        Returns:
            True if deleted.

        Raises:
            AuthorizationError: If not authorized.
            EntityNotFoundError: If user not found.
        """
        if not deleted_by.is_superuser:
            raise AuthorizationError("Only superusers can delete users.")

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", str(user_id))

        if user.id == deleted_by.id:
            raise AuthorizationError("Cannot delete yourself.")

        return self.user_repo.delete(user_id)
