import logging
from celery import shared_task
from typing import Any

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id: str) -> dict[str, Any]:
    """
    Send welcome email to a new user.

    This task is THIN - it only orchestrates. The actual email
    sending logic would be in an EmailService.

    Args:
        user_id: The user's UUID as string.

    Returns:
        Result dict with status.
    """
    try:
        # Import here to avoid circular imports
        from infrastructure.persistence.user_repository_impl import DjangoUserRepository

        user_repo = DjangoUserRepository()
        import uuid

        user = user_repo.get_by_id(uuid.UUID(user_id))

        if not user:
            logger.warning(f"User {user_id} not found for welcome email")
            return {"status": "skipped", "reason": "user_not_found"}

        # Here you would call an email service
        # email_service = EmailService()
        # email_service.send_welcome(user.email)

        logger.info(f"Welcome email sent to {user.email}")
        return {"status": "sent", "email": str(user.email)}

    except Exception as exc:
        logger.error(f"Failed to send welcome email: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_id: str, reset_token: str) -> dict[str, Any]:
    """
    Send password reset email.

    Args:
        user_id: The user's UUID as string.
        reset_token: The password reset token.

    Returns:
        Result dict with status.
    """
    try:
        from infrastructure.persistence.user_repository_impl import DjangoUserRepository
        import uuid

        user_repo = DjangoUserRepository()
        user = user_repo.get_by_id(uuid.UUID(user_id))

        if not user:
            return {"status": "skipped", "reason": "user_not_found"}

        # Send email via email service
        # email_service.send_password_reset(user.email, reset_token)

        logger.info(f"Password reset email sent to {user.email}")
        return {"status": "sent", "email": str(user.email)}

    except Exception as exc:
        logger.error(f"Failed to send password reset email: {exc}")
        raise self.retry(exc=exc, countdown=30)


@shared_task
def cleanup_inactive_users(days_inactive: int = 365) -> dict[str, Any]:
    """
    Periodic task to clean up long-inactive users.

    This is a scheduled task, not triggered by events.

    Args:
        days_inactive: Days of inactivity before cleanup.

    Returns:
        Result dict with count of affected users.
    """
    from datetime import datetime, timedelta, timezone
    from infrastructure.django.models.user_model import UserModel

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_inactive)

    # Find users who haven't logged in
    inactive_users = UserModel.objects.filter(
        last_login__lt=cutoff_date,
        is_active=True,
        is_staff=False,  # Never auto-deactivate staff
    )

    count = inactive_users.count()

    # Deactivate them (soft delete)
    inactive_users.update(is_active=False)

    logger.info(f"Deactivated {count} inactive users")
    return {"status": "completed", "deactivated_count": count}
