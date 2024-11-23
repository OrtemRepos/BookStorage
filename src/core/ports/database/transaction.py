from typing import Protocol


class TransactionInterface(Protocol):
    def commit(self):
        pass

    def roolback(self):
        pass
