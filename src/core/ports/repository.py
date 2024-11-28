from abc import abstractmethod
from typing import Protocol

from src.core.ports.database import TransactionInterface
from src.core.domain.book import Book
from src.core.dto.book_dto import BookDTO


class BookRepositoryInterface(Protocol):
    @abstractmethod
    def get(self, id: int, session: TransactionInterface) -> Book:
        pass

    @abstractmethod
    def create(self, book: BookDTO, session: TransactionInterface) -> int:
        pass

    @abstractmethod
    def update(self, book_id: int, book: BookDTO, session: TransactionInterface) -> Book:
        pass

    @abstractmethod
    def delete(self, id: int, session: TransactionInterface) -> None:
        pass
