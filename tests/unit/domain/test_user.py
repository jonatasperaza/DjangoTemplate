import uuid
from datetime import datetime, timezone

import pytest

from domain.entities.user import User
from domain.entities.value_objects import Email


class TestUserEntity:
    """Tests for User domain entity."""

    def test_create_user_with_defaults(self):
        """User should be created with sensible defaults."""
        user = User(email="test@example.com")

        assert user.email == Email("test@example.com")
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.password_hash is None
        assert isinstance(user.id, uuid.UUID)
        assert isinstance(user.created_at, datetime)

    def test_create_user_with_email_value_object(self):
        """User should accept Email value object."""
        email = Email("test@example.com")
        user = User(email=email)

        assert user.email == email

    def test_update_email_valid(self):
        """User should accept valid email update."""
        user = User(email="old@example.com")
        user.update_email("new@example.com")

        assert user.email == Email("new@example.com")

    def test_update_email_invalid(self):
        """User should reject invalid email format."""
        user = User(email="test@example.com")

        with pytest.raises(ValueError):
            user.update_email("invalid-email")

    def test_deactivate_regular_user(self):
        """Regular user can be deactivated."""
        user = User(email="test@example.com", is_staff=False)
        user.deactivate()

        assert user.is_active is False

    def test_deactivate_staff_user_raises(self):
        """Staff user cannot be directly deactivated."""
        user = User(email="admin@example.com", is_staff=True)

        with pytest.raises(PermissionError) as exc_info:
            user.deactivate()

        assert "Cannot deactivate staff user" in str(exc_info.value)

    def test_activate_user(self):
        """Inactive user can be activated."""
        user = User(email="test@example.com", is_active=False)
        user.activate()

        assert user.is_active is True

    def test_promote_to_staff(self):
        """Active user can be promoted to staff."""
        user = User(email="test@example.com", is_active=True)
        user.promote_to_staff()

        assert user.is_staff is True

    def test_promote_inactive_user_raises(self):
        """Inactive user cannot be promoted to staff."""
        user = User(email="test@example.com", is_active=False)

        with pytest.raises(PermissionError):
            user.promote_to_staff()

    def test_demote_from_staff(self):
        """Staff user can be demoted."""
        user = User(email="admin@example.com", is_staff=True)
        user.demote_from_staff()

        assert user.is_staff is False

    def test_set_password_hash(self):
        """User password hash can be set."""
        user = User(email="test@example.com")
        user.set_password_hash("hashed_password_here")

        assert user.password_hash == "hashed_password_here"

    def test_set_empty_password_hash_raises(self):
        """Empty password hash should raise error."""
        user = User(email="test@example.com")

        with pytest.raises(ValueError):
            user.set_password_hash("")

    def test_has_password(self):
        """Check if user has password set."""
        user = User(email="test@example.com")
        assert user.has_password() is False

        user.set_password_hash("some_hash")
        assert user.has_password() is True

    def test_record_login(self):
        """Recording login updates last_login."""
        user = User(email="test@example.com")
        assert user.last_login is None

        user.record_login()

        assert user.last_login is not None
        assert isinstance(user.last_login, datetime)

    def test_user_equality_by_id(self):
        """Two users with same ID are equal."""
        user_id = uuid.uuid4()
        user1 = User(id=user_id, email="test1@example.com")
        user2 = User(id=user_id, email="test2@example.com")

        assert user1 == user2

    def test_user_inequality_by_id(self):
        """Two users with different IDs are not equal."""
        user1 = User(email="test@example.com")
        user2 = User(email="test@example.com")

        assert user1 != user2

    def test_user_hashable(self):
        """Users should be hashable for use in sets."""
        user1 = User(email="test1@example.com")
        user2 = User(email="test2@example.com")

        user_set = {user1, user2}

        assert len(user_set) == 2
        assert user1 in user_set
