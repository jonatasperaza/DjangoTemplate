from typing import Any, Optional

from celery.result import AsyncResult

from application.ports.messaging import MessagingPort, DomainEvent, TaskResult
from infrastructure.messaging.celery_app import app


class CeleryMessagingAdapter(MessagingPort):
    """
    Messaging adapter using Celery.

    This adapter translates application-layer messaging operations
    to Celery task queue operations.
    """

    def publish_event(self, event: DomainEvent) -> None:
        """
        Publish a domain event for async processing.

        Routes the event to the appropriate handler task.

        Args:
            event: The domain event to publish.
        """
        # Send to generic event handler
        app.send_task(
            "infrastructure.messaging.tasks.events.handle_domain_event",
            args=[event.to_dict()],
        )

    def send_task(
        self,
        task_name: str,
        args: tuple = (),
        kwargs: Optional[dict[str, Any]] = None,
        countdown: Optional[int] = None,
        eta: Optional[Any] = None,
    ) -> TaskResult:
        """
        Send a task to the Celery queue.

        Args:
            task_name: The registered task name.
            args: Positional arguments for the task.
            kwargs: Keyword arguments for the task.
            countdown: Delay in seconds.
            eta: Exact execution time.

        Returns:
            TaskResult with task ID.
        """
        result = app.send_task(
            task_name,
            args=args,
            kwargs=kwargs or {},
            countdown=countdown,
            eta=eta,
        )

        return TaskResult(
            task_id=result.id,
            status="pending",
        )

    def get_task_status(self, task_id: str) -> str:
        """
        Get the status of a Celery task.

        Args:
            task_id: The task identifier.

        Returns:
            Status string.
        """
        result = AsyncResult(task_id, app=app)

        state_mapping = {
            "PENDING": "pending",
            "STARTED": "running",
            "RETRY": "running",
            "SUCCESS": "success",
            "FAILURE": "failure",
            "REVOKED": "failure",
        }

        return state_mapping.get(result.state, "unknown")
