from domain.entities.user import User
from domain.entities.value_objects import Email
from domain.exceptions import BusinessRuleViolationError


class UserDomainService:
    """
    Domain service for user-related business operations.

    This service contains business logic that spans multiple entities
    or doesn't naturally belong to a single entity.
    """

    @staticmethod
    def can_transfer_ownership(from_user: User, to_user: User) -> bool:
        """
        Check if ownership can be transferred between users.

        Business rules:
        - Both users must be active
        - Target user must not be staff (conflict of interest)
        - Source must be staff or superuser

        Args:
            from_user: Current owner.
            to_user: New owner.

        Returns:
            True if transfer is allowed.
        """
        if not from_user.is_active or not to_user.is_active:
            return False

        if to_user.is_staff:
            return False

        if not (from_user.is_staff or from_user.is_superuser):
            return False

        return True

    @staticmethod
    def validate_email_domain_policy(
        email: Email,
        allowed_domains: list[str] | None = None,
        blocked_domains: list[str] | None = None,
    ) -> None:
        """
        Validate email against domain policies.

        Args:
            email: Email to validate.
            allowed_domains: If provided, email domain must be in this list.
            blocked_domains: Email domain must not be in this list.

        Raises:
            BusinessRuleViolationError: If validation fails.
        """
        domain = email.domain.lower()

        if blocked_domains and domain in [d.lower() for d in blocked_domains]:
            raise BusinessRuleViolationError(
                rule="EMAIL_DOMAIN_BLOCKED", details=f"Domain '{domain}' is not allowed."
            )

        if allowed_domains:
            allowed = [d.lower() for d in allowed_domains]
            if domain not in allowed:
                raise BusinessRuleViolationError(
                    rule="EMAIL_DOMAIN_NOT_ALLOWED",
                    details=f"Domain '{domain}' is not in the allowed list.",
                )

    @staticmethod
    def calculate_user_tier(user: User, total_spend_cents: int) -> str:
        """
        Calculate user loyalty tier based on spend.

        This is an example of domain logic that involves calculations
        based on entity state and external data.

        Args:
            user: The user entity.
            total_spend_cents: Total amount spent in cents.

        Returns:
            Tier name: 'bronze', 'silver', 'gold', 'platinum'.
        """
        if not user.is_active:
            return "inactive"

        if user.is_staff:
            return "staff"

        # Tier thresholds in cents
        if total_spend_cents >= 1_000_000:  # R$ 10.000+
            return "platinum"
        elif total_spend_cents >= 500_000:  # R$ 5.000+
            return "gold"
        elif total_spend_cents >= 100_000:  # R$ 1.000+
            return "silver"
        else:
            return "bronze"
