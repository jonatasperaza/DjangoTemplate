from domain.entities.user import User
from domain.entities.value_objects import Email
from infrastructure.django.models.user_model import UserModel


class UserMapper:
    """
    Bidirectional mapper between UserModel and User entity.

    This class is stateless - all methods are static.
    """

    @staticmethod
    def to_entity(model: UserModel) -> User:
        """
        Convert a Django UserModel to a domain User entity.

        Args:
            model: The Django UserModel instance.

        Returns:
            A domain User entity.
        """
        return User(
            id=model.id,
            email=Email(model.email),
            is_active=model.is_active,
            is_staff=model.is_staff,
            is_superuser=model.is_superuser,
            created_at=model.date_joined,
            updated_at=model.updated_at,
            password_hash=model.password,
            last_login=model.last_login,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        """
        Convert a domain User entity to a Django UserModel.

        Note: This creates a NEW model instance. For updates, use update_model().

        Args:
            entity: The domain User entity.

        Returns:
            A Django UserModel instance (not saved).
        """
        return UserModel(
            id=entity.id,
            email=str(entity.email),
            is_active=entity.is_active,
            is_staff=entity.is_staff,
            is_superuser=entity.is_superuser,
            password=entity.password_hash or "",
            date_joined=entity.created_at,
            last_login=entity.last_login,
        )

    @staticmethod
    def update_model(model: UserModel, entity: User) -> UserModel:
        """
        Update an existing Django UserModel with entity data.

        This preserves the model's identity and only updates fields.

        Args:
            model: The existing UserModel to update.
            entity: The domain User entity with new data.

        Returns:
            The updated UserModel instance (not saved).
        """
        model.email = str(entity.email)
        model.is_active = entity.is_active
        model.is_staff = entity.is_staff
        model.is_superuser = entity.is_superuser
        model.last_login = entity.last_login

        # Only update password if it changed
        if entity.password_hash and entity.password_hash != model.password:
            model.password = entity.password_hash

        return model
