from src.core.dto.book_dto import ReadBookDTO
from src.core.ports.database import TransactionInterface
from src.core.service.book_service import BookService


class getBookUsecase:
    def __init__(self, service: BookService):
        self.service = service

    def execute(self, id: int, session: TransactionInterface) -> ReadBookDTO:
        return self.service.get(id, session)
