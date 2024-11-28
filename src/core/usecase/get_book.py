from src.core.domain.book import Book
from src.core.ports.database import TransactionInterface
from src.core.ports.repository import BookRepositoryInterface


class getBookUsecase:
    def __init__(self, repository: BookRepositoryInterface):
        self.repository = repository

    def execute(self, id: int, session: TransactionInterface) -> Book:
        return self.repository.get(id, session)
