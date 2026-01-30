from django.db import transaction

from domain.repositories.unit_of_work import UnitOfWork
from domain.repositories.user_repository import UserRepository
from infrastructure.persistence.user_repository_impl import DjangoUserRepository


class DjangoUnitOfWork(UnitOfWork):
    """
    Unit of Work implementation using Django transactions.

    Usage:
        with DjangoUnitOfWork() as uow:
            user = uow.users.get_by_email("test@example.com")
            user.deactivate()
            uow.users.save(user)
            uow.commit()
    """

    def __init__(self) -> None:
        self._users: UserRepository | None = None
        self._atomic: transaction.Atomic | None = None

    @property
    def users(self) -> UserRepository:
        """Get the user repository."""
        if self._users is None:
            self._users = DjangoUserRepository()
        return self._users

    def __enter__(self) -> "DjangoUnitOfWork":
        """Start a database transaction."""
        self._atomic = transaction.atomic()
        self._atomic.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        End the transaction.

        If an exception occurred, Django will automatically rollback.
        Otherwise, changes are committed when commit() is called.
        """
        if self._atomic:
            self._atomic.__exit__(exc_type, exc_val, exc_tb)

    def commit(self) -> None:
        """
        Commit the transaction.

        Note: Django's atomic() automatically commits on successful context exit.
        This method is here for explicit semantics and future flexibility.
        """
        # Django handles commit automatically when atomic() exits without exception
        pass

    def rollback(self) -> None:
        """
        Rollback the transaction.

        Raises an exception to trigger Django's transaction rollback.
        """
        transaction.set_rollback(True)
