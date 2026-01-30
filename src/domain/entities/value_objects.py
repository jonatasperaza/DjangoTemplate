from dataclasses import dataclass
import re
from typing import Any


@dataclass(frozen=True)
class Email:
    """
    Email Value Object.

    Immutable representation of an email address with validation.
    """

    value: str

    _EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __post_init__(self) -> None:
        """Validate email format after initialization."""
        if self.value and not self._EMAIL_REGEX.match(self.value):
            raise ValueError(f"Invalid email format: {self.value}")

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Email):
            return self.value.lower() == other.value.lower()
        if isinstance(other, str):
            return self.value.lower() == other.lower()
        return False

    def __hash__(self) -> int:
        return hash(self.value.lower())

    @property
    def domain(self) -> str:
        """Extract the domain part of the email."""
        if "@" in self.value:
            return self.value.split("@")[1]
        return ""

    @property
    def local_part(self) -> str:
        """Extract the local part (before @) of the email."""
        if "@" in self.value:
            return self.value.split("@")[0]
        return self.value


@dataclass(frozen=True)
class Password:
    """
    Password Value Object.

    Represents a plain-text password with strength validation.
    This is used for validation before hashing - never store plain passwords!
    """

    value: str

    MIN_LENGTH = 8
    MAX_LENGTH = 128

    def __post_init__(self) -> None:
        """Validate password strength."""
        errors: list[str] = []

        if len(self.value) < self.MIN_LENGTH:
            errors.append(f"Password must be at least {self.MIN_LENGTH} characters.")

        if len(self.value) > self.MAX_LENGTH:
            errors.append(f"Password must be at most {self.MAX_LENGTH} characters.")

        if not any(c.isupper() for c in self.value):
            errors.append("Password must contain at least one uppercase letter.")

        if not any(c.islower() for c in self.value):
            errors.append("Password must contain at least one lowercase letter.")

        if not any(c.isdigit() for c in self.value):
            errors.append("Password must contain at least one digit.")

        if errors:
            raise ValueError(" ".join(errors))

    def __str__(self) -> str:
        """Never expose the actual password in string representation."""
        return "********"

    def __repr__(self) -> str:
        """Never expose the actual password in repr."""
        return "Password(********)"


@dataclass(frozen=True)
class Money:
    """
    Money Value Object.

    Represents a monetary amount with currency.
    Uses integer cents to avoid floating point issues.
    """

    amount_cents: int
    currency: str = "BRL"

    SUPPORTED_CURRENCIES = {"BRL", "USD", "EUR", "GBP"}

    def __post_init__(self) -> None:
        """Validate money attributes."""
        if self.currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(
                f"Unsupported currency: {self.currency}. Supported: {self.SUPPORTED_CURRENCIES}"
            )

    @classmethod
    def from_decimal(cls, amount: float, currency: str = "BRL") -> "Money":
        """Create Money from decimal amount (e.g., 10.50 -> 1050 cents)."""
        return cls(amount_cents=int(amount * 100), currency=currency)

    def to_decimal(self) -> float:
        """Convert to decimal amount."""
        return self.amount_cents / 100

    def __add__(self, other: "Money") -> "Money":
        """Add two Money objects."""
        if not isinstance(other, Money):
            raise TypeError(f"Cannot add Money and {type(other)}")
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies.")
        return Money(self.amount_cents + other.amount_cents, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        """Subtract two Money objects."""
        if not isinstance(other, Money):
            raise TypeError(f"Cannot subtract Money and {type(other)}")
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies.")
        return Money(self.amount_cents - other.amount_cents, self.currency)

    def __str__(self) -> str:
        """Format as currency string."""
        symbols = {"BRL": "R$", "USD": "$", "EUR": "€", "GBP": "£"}
        symbol = symbols.get(self.currency, self.currency)
        return f"{symbol} {self.to_decimal():.2f}"
