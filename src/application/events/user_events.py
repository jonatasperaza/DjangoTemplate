from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class UserEvent:
    """Base class for user-related events."""

    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)

    @property
    def event_type(self) -> str:
        return self.__class__.__name__

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "user_id": str(self.user_id),
        }


@dataclass
class UserRegistered(UserEvent):
    """Published when a new user registers."""

    email: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["email"] = self.email
        return data


@dataclass
class UserLoggedIn(UserEvent):
    """Published when a user successfully logs in."""

    ip_address: str | None = None
    user_agent: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["ip_address"] = self.ip_address
        data["user_agent"] = self.user_agent
        return data


@dataclass
class UserLoggedOut(UserEvent):
    """Published when a user logs out."""

    pass


@dataclass
class UserDeactivated(UserEvent):
    """Published when a user is deactivated."""

    deactivated_by: uuid.UUID = field(default_factory=uuid.uuid4)
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["deactivated_by"] = str(self.deactivated_by)
        data["reason"] = self.reason
        return data


@dataclass
class UserPasswordChanged(UserEvent):
    """Published when a user changes their password."""

    pass


@dataclass
class UserEmailChanged(UserEvent):
    """Published when a user changes their email."""

    old_email: str = ""
    new_email: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["old_email"] = self.old_email
        data["new_email"] = self.new_email
        return data
