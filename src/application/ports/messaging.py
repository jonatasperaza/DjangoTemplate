from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class TaskResult:
    """Result of an async task submission."""

    task_id: str
    status: str = "pending"


@dataclass
class DomainEvent:
    """
    Base class for domain events.

    Domain events represent something that happened in the domain
    that other parts of the system might be interested in.
    """

    event_type: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "payload": self.payload,
        }


class MessagingPort(ABC):
    """
    Abstract interface for messaging and task queue operations.
    """

    @abstractmethod
    def publish_event(self, event: DomainEvent) -> None:
        """
        Publish a domain event for async processing.

        Args:
            event: The domain event to publish.
        """
        ...

    @abstractmethod
    def send_task(
        self,
        task_name: str,
        args: tuple = (),
        kwargs: Optional[dict[str, Any]] = None,
        countdown: Optional[int] = None,
        eta: Optional[Any] = None,
    ) -> TaskResult:
        """
        Send a task to the async queue.

        Args:
            task_name: The registered task name.
            args: Positional arguments for the task.
            kwargs: Keyword arguments for the task.
            countdown: Delay in seconds before executing.
            eta: Exact time to execute (datetime).

        Returns:
            TaskResult with task ID and initial status.
        """
        ...

    @abstractmethod
    def get_task_status(self, task_id: str) -> str:
        """
        Get the status of a submitted task.

        Args:
            task_id: The task identifier.

        Returns:
            Status string: 'pending', 'running', 'success', 'failure'.
        """
        ...
