from src.core.dto.book_dto import BookDTO
from src.core.ports.database import TransactionInterface
from src.core.service.book_service import BookService


class addBookUsecase:
    def __init__(self, service: BookService):
        self.service = service

    def execute(self, book: BookDTO, session: TransactionInterface) -> int:
        return self.service.create(book, session)
