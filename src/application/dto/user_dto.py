from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
import uuid


class UserCreateInput(BaseModel):
    """Input DTO for creating a user (admin operation)."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    is_staff: bool = False
    is_active: bool = True


class UserUpdateInput(BaseModel):
    """Input DTO for updating user data."""

    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_staff: Optional[bool] = None


class UserListInput(BaseModel):
    """Input DTO for listing users with pagination."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    active_only: bool = True


class UserListOutput(BaseModel):
    """Output DTO for paginated user list."""

    users: list["UserOutput"]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserOutput(BaseModel):
    """Output DTO for user data."""

    id: uuid.UUID
    email: str
    is_active: bool
    is_staff: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Update forward reference
UserListOutput.model_rebuild()
