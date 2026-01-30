from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid


class UserManager(BaseUserManager):
    """
    Custom user manager that uses email as the unique identifier.
    """

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        """
        Create and save a regular user.

        Args:
            email: User's email address.
            password: Plain text password (will be hashed).
            **extra_fields: Additional fields to set.

        Returns:
            The created UserModel instance.
        """
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        """
        Create and save a superuser.

        Args:
            email: User's email address.
            password: Plain text password (will be hashed).
            **extra_fields: Additional fields to set.

        Returns:
            The created superuser UserModel instance.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class UserModel(AbstractUser):
    """
    Custom User model that uses email as the primary identifier.

    This is a persistence ADAPTER - it implements the storage mechanism
    for our domain User entity. The domain entity is completely unaware
    of this model.

    Mapping:
        Domain User.id -> UserModel.id
        Domain User.email -> UserModel.email
        Domain User.is_active -> UserModel.is_active
        Domain User.is_staff -> UserModel.is_superuser (intentional mapping)
        Domain User.password_hash -> UserModel.password
        Domain User.created_at -> UserModel.date_joined
        Domain User.updated_at -> UserModel.updated_at
    """

    # Override id to use UUID
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the user",
    )

    # Use email as the unique identifier instead of username
    email = models.EmailField(
        unique=True,
        db_index=True,
        help_text="User's email address (used for login)",
    )

    # Remove username field - we use email
    username = None

    # Additional fields not in domain but useful for infrastructure
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of last successful login",
    )

    email_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the email was verified",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp",
    )

    # Use email for authentication
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # email is already required by USERNAME_FIELD

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"
        indexes = [
            models.Index(fields=["email", "is_active"]),
            models.Index(fields=["is_active", "is_staff"]),
        ]
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return self.email

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email})>"
