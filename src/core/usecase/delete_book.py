from src.core.ports.database import TransactionInterface
from src.core.ports.repository import BookRepositoryInterface


class deleteBookUsecase:
    def __init__(self, repository: BookRepositoryInterface):
        self.repository = repository

    def execute(self, id: int, session: TransactionInterface):
        self.repository.delete(id, session)
