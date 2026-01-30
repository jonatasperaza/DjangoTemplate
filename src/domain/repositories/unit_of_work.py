from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.repositories.user_repository import UserRepository


class UnitOfWork(ABC):
    """
    Abstract Unit of Work interface.

    Provides transaction management across multiple repositories.
    Use as a context manager:

        with uow:
            user = uow.users.get_by_email("test@example.com")
            user.deactivate()
            uow.users.save(user)
            uow.commit()
    """

    users: "UserRepository"

    @abstractmethod
    def __enter__(self) -> "UnitOfWork":
        """Start a new unit of work (transaction)."""
        ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        End the unit of work.

        If an exception occurred, rollback. Otherwise, the transaction
        remains open until commit() is called.
        """
        ...

    @abstractmethod
    def commit(self) -> None:
        """
        Commit the current transaction.

        Persists all changes made within the unit of work.
        """
        ...

    @abstractmethod
    def rollback(self) -> None:
        """
        Rollback the current transaction.

        Discards all changes made within the unit of work.
        """
        ...
