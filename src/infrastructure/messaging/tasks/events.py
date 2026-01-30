import logging
from typing import Any

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def handle_domain_event(event_data: dict[str, Any]) -> dict[str, Any]:
    """
    Generic handler for domain events.

    Routes events to specific handlers based on event_type.

    Args:
        event_data: The event dictionary with event_type and payload.

    Returns:
        Result dict with handling status.
    """
    event_type = event_data.get("event_type", "unknown")
    payload = event_data.get("payload", {})

    logger.info(f"Handling domain event: {event_type}")

    # Route to specific handlers
    handlers = {
        "user.registered": handle_user_registered,
        "user.logged_in": handle_user_logged_in,
        "user.password_changed": handle_password_changed,
    }

    handler = handlers.get(event_type)

    if handler:
        return handler(payload)
    else:
        logger.warning(f"No handler for event type: {event_type}")
        return {"status": "ignored", "reason": "no_handler"}


def handle_user_registered(payload: dict[str, Any]) -> dict[str, Any]:
    """Handle user registration event."""
    user_id = payload.get("user_id")
    email = payload.get("email")

    logger.info(f"New user registered: {email}")

    # Trigger welcome email
    from infrastructure.messaging.tasks.user_tasks import send_welcome_email

    send_welcome_email.delay(user_id)

    return {"status": "handled", "action": "welcome_email_queued"}


def handle_user_logged_in(payload: dict[str, Any]) -> dict[str, Any]:
    """Handle user login event."""
    user_id = payload.get("user_id")

    logger.info(f"User logged in: {user_id}")

    # Could track login analytics, update last_login_ip, etc.
    return {"status": "handled", "action": "login_recorded"}


def handle_password_changed(payload: dict[str, Any]) -> dict[str, Any]:
    """Handle password change event."""
    user_id = payload.get("user_id")

    logger.info(f"Password changed for user: {user_id}")

    # Could send security notification email
    return {"status": "handled", "action": "security_notification_sent"}
