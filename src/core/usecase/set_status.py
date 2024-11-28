from src.core.domain.book import Book, BookStatus
from src.core.ports.database import TransactionInterface
from src.core.service.book_service import BookService


class setBookStatusUsecase:
    def __init__(self, service: BookService):
        self.service = service

    def execute(self, id: int, status: BookStatus, session: TransactionInterface) -> Book:
        return self.service.set_status(id, status, session)
