from abc import abstractmethod
from typing import Protocol

from src.core.domain.book import Book
from src.core.dto.book_dto import BookDTO


class BookRepositoryInterface(Protocol):
    @abstractmethod
    def get(self, id: int) -> Book:
        pass

    @abstractmethod
    def create(self, book: BookDTO) -> int:
        pass

    @abstractmethod
    def update(self, book_id: int, book: BookDTO) -> Book:
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        pass
