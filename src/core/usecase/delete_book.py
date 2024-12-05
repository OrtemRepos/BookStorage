from src.core.ports.database import TransactionInterface
from src.core.service.book_service import BookService


class deleteBookUsecase:
    def __init__(self, service: BookService):
        self.service = service

    def execute(self, id: int, session: TransactionInterface):
        self.service.delete(id, session)
