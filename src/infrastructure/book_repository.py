from src.core.domain.book import Book
from src.core.dto.book_dto import BookDTO
from src.core.ports.database import TransactionInterface
from src.core.ports.repository import BookRepositoryInterface


class BookRepository(BookRepositoryInterface):
    def get(self, id: int, session: TransactionInterface) -> Book:
        data = session.get(id)
        if isinstance(data, dict):
            book = Book.from_dict(data)
        else:
            raise Exception
        return book

    def create(self, book: BookDTO, session: TransactionInterface) -> int:
        return session.create(book)

    def update(self, book_id: int, book: BookDTO, session: TransactionInterface) -> Book:
        if session.get(book_id) is None:
            raise Exception("Book not found")
        else:
            book_with_id = Book(id=book_id, **book.__dict__)
            session.set(book_id, book_with_id)
        return self.get(book_id, session)

    def delete(self, id: int, session: TransactionInterface) -> None:
        session.delete(id)
