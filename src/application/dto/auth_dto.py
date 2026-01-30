from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import uuid


class LoginInput(BaseModel):
    """Input DTO for login operation."""

    email: EmailStr
    password: str = Field(..., min_length=1)
    remember_me: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
                "remember_me": True,
            }
        }
    }


class LoginOutput(BaseModel):
    """Output DTO for successful login."""

    user_id: uuid.UUID
    email: str
    access_expires_in: int  # seconds
    refresh_expires_in: int  # seconds

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "access_expires_in": 900,
                "refresh_expires_in": 604800,
            }
        }
    }


class RefreshInput(BaseModel):
    """Input DTO for token refresh operation."""

    # Refresh token comes from HttpOnly cookie, not body
    # This DTO is mainly for documentation :)
    pass


class RefreshOutput(BaseModel):
    """Output DTO for token refresh."""

    access_expires_in: int


class RegisterInput(BaseModel):
    """Input DTO for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password has required characters."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Validate passwords match."""
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class RegisterOutput(BaseModel):
    """Output DTO for successful registration."""

    user_id: uuid.UUID
    email: str
    created_at: datetime


class UserOutput(BaseModel):
    """Output DTO for user data."""

    id: uuid.UUID
    email: str
    is_active: bool
    is_staff: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {
        "from_attributes": True  # Allow creating from ORM models
    }


class ChangePasswordInput(BaseModel):
    """Input DTO for password change."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    new_password_confirm: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password has required characters."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("new_password_confirm")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Validate passwords match."""
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v
