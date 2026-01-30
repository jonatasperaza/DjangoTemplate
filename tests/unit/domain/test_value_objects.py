import pytest

from domain.entities.value_objects import Email, Password, Money


class TestEmailValueObject:
    """Tests for Email value object."""

    def test_valid_email(self):
        """Valid email should be accepted."""
        email = Email("test@example.com")
        assert email.value == "test@example.com"

    def test_invalid_email_format(self):
        """Invalid email format should raise ValueError."""
        with pytest.raises(ValueError):
            Email("invalid-email")

    def test_invalid_email_no_domain(self):
        """Email without domain should raise ValueError."""
        with pytest.raises(ValueError):
            Email("test@")

    def test_empty_email_allowed(self):
        """Empty email is allowed (for optional fields)."""
        email = Email("")
        assert email.value == ""

    def test_email_str_representation(self):
        """Email should have proper string representation."""
        email = Email("test@example.com")
        assert str(email) == "test@example.com"

    def test_email_equality(self):
        """Emails are equal if values match (case-insensitive)."""
        email1 = Email("Test@Example.com")
        email2 = Email("test@example.com")

        assert email1 == email2

    def test_email_equality_with_string(self):
        """Email can be compared with string."""
        email = Email("test@example.com")
        assert email == "test@example.com"
        assert email == "TEST@EXAMPLE.COM"

    def test_email_domain_extraction(self):
        """Domain should be extracted correctly."""
        email = Email("user@example.com")
        assert email.domain == "example.com"

    def test_email_local_part_extraction(self):
        """Local part should be extracted correctly."""
        email = Email("user@example.com")
        assert email.local_part == "user"

    def test_email_is_hashable(self):
        """Email should be hashable for use in sets/dicts."""
        email1 = Email("test@example.com")
        email2 = Email("other@example.com")

        email_set = {email1, email2}
        assert len(email_set) == 2

    def test_email_is_immutable(self):
        """Email should be immutable (frozen dataclass)."""
        email = Email("test@example.com")

        with pytest.raises(AttributeError):
            email.value = "new@example.com"


class TestPasswordValueObject:
    """Tests for Password value object."""

    def test_valid_password(self):
        """Valid password should be accepted."""
        password = Password("SecurePass123")
        assert password.value == "SecurePass123"

    def test_password_too_short(self):
        """Password shorter than 8 chars should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            Password("Short1")

        assert "at least 8 characters" in str(exc_info.value)

    def test_password_no_uppercase(self):
        """Password without uppercase should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            Password("nouppercase123")

        assert "uppercase" in str(exc_info.value)

    def test_password_no_lowercase(self):
        """Password without lowercase should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            Password("NOLOWERCASE123")

        assert "lowercase" in str(exc_info.value)

    def test_password_no_digit(self):
        """Password without digit should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            Password("NoDigitsHere")

        assert "digit" in str(exc_info.value)

    def test_password_str_hidden(self):
        """Password string representation should hide value."""
        password = Password("SecurePass123")
        assert str(password) == "********"
        assert "SecurePass123" not in str(password)

    def test_password_repr_hidden(self):
        """Password repr should hide value."""
        password = Password("SecurePass123")
        assert "SecurePass123" not in repr(password)


class TestMoneyValueObject:
    """Tests for Money value object."""

    def test_create_money_in_cents(self):
        """Money should store amount in cents."""
        money = Money(amount_cents=1050)
        assert money.amount_cents == 1050

    def test_create_money_from_decimal(self):
        """Money can be created from decimal amount."""
        money = Money.from_decimal(10.50)
        assert money.amount_cents == 1050

    def test_money_to_decimal(self):
        """Money can be converted to decimal."""
        money = Money(amount_cents=1050)
        assert money.to_decimal() == 10.50

    def test_money_default_currency(self):
        """Default currency should be BRL."""
        money = Money(amount_cents=100)
        assert money.currency == "BRL"

    def test_money_custom_currency(self):
        """Custom currency should be accepted."""
        money = Money(amount_cents=100, currency="USD")
        assert money.currency == "USD"

    def test_money_unsupported_currency(self):
        """Unsupported currency should raise error."""
        with pytest.raises(ValueError):
            Money(amount_cents=100, currency="XYZ")

    def test_money_addition(self):
        """Money can be added."""
        m1 = Money(amount_cents=100)
        m2 = Money(amount_cents=50)
        result = m1 + m2

        assert result.amount_cents == 150
        assert result.currency == "BRL"

    def test_money_addition_different_currencies(self):
        """Cannot add different currencies."""
        m1 = Money(amount_cents=100, currency="BRL")
        m2 = Money(amount_cents=50, currency="USD")

        with pytest.raises(ValueError):
            m1 + m2

    def test_money_subtraction(self):
        """Money can be subtracted."""
        m1 = Money(amount_cents=100)
        m2 = Money(amount_cents=30)
        result = m1 - m2

        assert result.amount_cents == 70

    def test_money_str_format_brl(self):
        """BRL money should format with R$ symbol."""
        money = Money(amount_cents=1050, currency="BRL")
        assert str(money) == "R$ 10.50"

    def test_money_str_format_usd(self):
        """USD money should format with $ symbol."""
        money = Money(amount_cents=1050, currency="USD")
        assert str(money) == "$ 10.50"
