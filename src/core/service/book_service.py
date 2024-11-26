from src.core.dto.book_dto import BookDTO, ReadBookDTO
from src.core.ports.repository.uow import BookUnitOfWorkInterface


class BookService:
    def __init__(self, uow: BookUnitOfWorkInterface):
        self.uow = uow

    def create(self, book: BookDTO) -> int:
        with self.uow as repository:
            return repository.create(book)

    def update(self, book_id: int, book: BookDTO) -> ReadBookDTO:
        with self.uow as repository:
            result = repository.update(book_id, book)
        return ReadBookDTO(**result.to_dict())

    def delete(self, id: int):
        with self.uow as repository:
            repository.delete(id)

    def get(self, id: int) -> ReadBookDTO:
        with self.uow as repository:
            result = repository.get(id)
            return ReadBookDTO(**result.to_dict())
