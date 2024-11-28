from src.core.domain.book import Book, BookStatus
from src.core.dto.book_dto import BookDTO, ReadBookDTO
from src.core.ports.repository import BookRepositoryInterface, TransactionInterface


class BookService:
    def __init__(self, repository: BookRepositoryInterface):
        self.repository = repository

    def create(self, book: BookDTO, session: TransactionInterface) -> int:
        return self.repository.create(book, session)

    def set_status(self, id: int, status: BookStatus, session: TransactionInterface) -> Book:
        old_book = self.repository.get(id, session)
        new_book = BookDTO(
            title=old_book.title, author=old_book.author, year=old_book.year, status=status
        )
        return self.repository.update(id, new_book, session)

    def delete(self, id: int, session: TransactionInterface):
        self.repository.delete(id, session)

    def get(self, id: int, session: TransactionInterface) -> ReadBookDTO:
        result = self.repository.get(id, session)
        return ReadBookDTO(**result.to_dict())
