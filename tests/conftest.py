import os
import sys
from pathlib import Path

import pytest

# Add src to path
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infrastructure.django.settings.local")


@pytest.fixture(scope="session")
def django_db_setup():
    """Configure Django database for testing."""
    import django

    django.setup()


@pytest.fixture
def user_data():
    """Sample user data for tests."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123",
    }


@pytest.fixture
def create_user(db):
    """Factory fixture to create users."""
    from infrastructure.django.models.user_model import UserModel

    def _create_user(email="test@example.com", password="SecurePass123", **kwargs):
        return UserModel.objects.create_user(email=email, password=password, **kwargs)

    return _create_user
