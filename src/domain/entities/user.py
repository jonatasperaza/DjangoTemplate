from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid

from domain.entities.value_objects import Email


@dataclass
class User:
    """
    User domain entity.

    This is the core User representation in our domain. It knows nothing about
    Django, databases, or HTTP. All business rules related to users live here.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    email: Email = field(default_factory=lambda: Email(""))
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    password_hash: Optional[str] = None
    last_login: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate entity after initialization."""
        if isinstance(self.email, str):
            self.email = Email(self.email)

    def update_email(self, new_email: str) -> None:
        """
        Update user's email address.

        Args:
            new_email: The new email address.

        Raises:
            ValueError: If the email format is invalid.
        """
        self.email = Email(new_email)
        self._touch()

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        self._touch()

    def deactivate(self) -> None:
        """
        Deactivate the user account.

        Raises:
            PermissionError: If trying to deactivate a staff user directly.
        """
        if self.is_staff:
            raise PermissionError(
                "Cannot deactivate staff user directly. Remove staff status first."
            )
        self.is_active = False
        self._touch()

    def promote_to_staff(self) -> None:
        """Promote user to staff status."""
        if not self.is_active:
            raise PermissionError("Cannot promote inactive user to staff.")
        self.is_staff = True
        self._touch()

    def demote_from_staff(self) -> None:
        """Remove staff status from user."""
        self.is_staff = False
        self._touch()

    def record_login(self) -> None:
        """Record a successful login."""
        self.last_login = datetime.now(timezone.utc)

    def set_password_hash(self, password_hash: str) -> None:
        """
        Set the password hash.

        Note: The actual hashing is done by the security port in the
        infrastructure layer. The domain only stores the hash.
        """
        if not password_hash:
            raise ValueError("Password hash cannot be empty.")
        self.password_hash = password_hash
        self._touch()

    def has_password(self) -> bool:
        """Check if user has a password set."""
        return self.password_hash is not None and len(self.password_hash) > 0

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    def __eq__(self, other: object) -> bool:
        """Two users are equal if they have the same ID."""
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID for use in sets and dicts."""
        return hash(self.id)
