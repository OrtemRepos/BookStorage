from src.core.ports.repository.uow import BookUnitOfWorkInterface
from src.core.domain.book import Book
from src.core.dto.book_dto import BookDTO, ReadBookDTO


class BookService:
    def __init__(self, uow: BookUnitOfWorkInterface):
        self.uow = uow

    def create(self, book: Book) -> int:
        with self.uow as repository:
            return repository.create(book)

    def update(self, book_id: int, book: BookDTO) -> ReadBookDTO:
        with self.uow as repository:
            result: Book = repository.update(book_id, book)
        return ReadBookDTO(result.to_dict())

    def delete(self, id: int):
        with self.uow as repository:
            repository.delete(id)

    def get(self, id: int) -> ReadBookDTO:
        with self.uow as repository:
            result: Book = repository.get(id)
            return ReadBookDTO(result.to_dict())
