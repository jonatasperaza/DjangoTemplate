from django.apps import AppConfig


class InfrastructureConfig(AppConfig):
    """Configuration for the infrastructure Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "infrastructure.django"
    label = "django_infra"  # Shorter label for migrations and references
    verbose_name = "Infrastructure"

    def ready(self) -> None:
        """
        Called when Django starts.

        This is a good place to:
        - Import signal handlers
        - Initialize Celery
        - Set up any other infrastructure
        """
        # Import signals if you have any
        # from infrastructure.django import signals  # noqa: F401
        pass
