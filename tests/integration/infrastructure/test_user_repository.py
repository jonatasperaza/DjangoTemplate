import uuid

import pytest
from django.test import TestCase

from domain.entities.user import User
from domain.entities.value_objects import Email
from infrastructure.persistence.user_repository_impl import DjangoUserRepository
from infrastructure.django.models.user_model import UserModel


@pytest.mark.django_db
class TestDjangoUserRepository:
    """Integration tests for DjangoUserRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = DjangoUserRepository()

    def test_save_new_user(self):
        """New user should be persisted correctly."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
        )

        saved_user = self.repo.save(user)

        assert saved_user.id == user.id
        assert saved_user.email == Email("test@example.com")

        # Verify in database
        model = UserModel.objects.get(id=user.id)
        assert model.email == "test@example.com"

    def test_save_update_existing_user(self):
        """Existing user should be updated correctly."""
        # Create user
        user = User(email="test@example.com")
        self.repo.save(user)

        # Update user
        user.update_email("updated@example.com")
        self.repo.save(user)

        # Verify update
        retrieved = self.repo.get_by_id(user.id)
        assert retrieved.email == Email("updated@example.com")

    def test_get_by_id_existing(self):
        """Existing user should be retrieved by ID."""
        user = User(email="test@example.com")
        self.repo.save(user)

        retrieved = self.repo.get_by_id(user.id)

        assert retrieved is not None
        assert retrieved.id == user.id
        assert retrieved.email == user.email

    def test_get_by_id_not_found(self):
        """Non-existent user should return None."""
        result = self.repo.get_by_id(uuid.uuid4())
        assert result is None

    def test_get_by_email_existing(self):
        """Existing user should be retrieved by email."""
        user = User(email="test@example.com")
        self.repo.save(user)

        retrieved = self.repo.get_by_email("test@example.com")

        assert retrieved is not None
        assert retrieved.id == user.id

    def test_get_by_email_case_insensitive(self):
        """Email lookup should be case-insensitive."""
        user = User(email="Test@Example.com")
        self.repo.save(user)

        retrieved = self.repo.get_by_email("TEST@EXAMPLE.COM")

        assert retrieved is not None
        assert retrieved.id == user.id

    def test_get_by_email_not_found(self):
        """Non-existent email should return None."""
        result = self.repo.get_by_email("nonexistent@example.com")
        assert result is None

    def test_exists_by_email(self):
        """Should correctly check if email exists."""
        user = User(email="test@example.com")
        self.repo.save(user)

        assert self.repo.exists_by_email("test@example.com") is True
        assert self.repo.exists_by_email("other@example.com") is False

    def test_delete_existing_user(self):
        """Existing user should be deleted."""
        user = User(email="test@example.com")
        self.repo.save(user)

        result = self.repo.delete(user.id)

        assert result is True
        assert self.repo.get_by_id(user.id) is None

    def test_delete_non_existent_user(self):
        """Deleting non-existent user should return False."""
        result = self.repo.delete(uuid.uuid4())
        assert result is False

    def test_list_active_users(self):
        """Should list only active users."""
        # Create active users
        for i in range(3):
            user = User(email=f"active{i}@example.com", is_active=True)
            self.repo.save(user)

        # Create inactive user
        inactive = User(email="inactive@example.com", is_active=False)
        self.repo.save(inactive)

        active_users = self.repo.list_active()

        assert len(active_users) == 3
        assert all(u.is_active for u in active_users)

    def test_list_active_with_pagination(self):
        """Should paginate active users correctly."""
        # Create 5 users
        for i in range(5):
            user = User(email=f"user{i}@example.com")
            self.repo.save(user)

        # Get first page
        page1 = self.repo.list_active(limit=2, offset=0)
        assert len(page1) == 2

        # Get second page
        page2 = self.repo.list_active(limit=2, offset=2)
        assert len(page2) == 2

        # Ensure no overlap
        page1_ids = {u.id for u in page1}
        page2_ids = {u.id for u in page2}
        assert page1_ids.isdisjoint(page2_ids)

    def test_count_active_users(self):
        """Should count only active users."""
        # Create 3 active, 2 inactive
        for i in range(3):
            user = User(email=f"active{i}@example.com", is_active=True)
            self.repo.save(user)

        for i in range(2):
            user = User(email=f"inactive{i}@example.com", is_active=False)
            self.repo.save(user)

        count = self.repo.count_active()
        assert count == 3
