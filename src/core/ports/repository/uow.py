from abc import abstractmethod
from typing import Protocol

from src.core.ports.repository.repository import BookRepositoryInterface


class BookUnitOfWorkInterface(Protocol):
    @abstractmethod
    def __init__(self, book_repository: BookRepositoryInterface) -> None:
        pass

    @abstractmethod
    def __enter__(self) -> BookRepositoryInterface:
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass
