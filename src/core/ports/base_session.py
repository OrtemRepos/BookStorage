from typing import Protocol


class SessionInterface(Protocol):
    def commit(self):
        pass

    def rollback(self):
        pass
