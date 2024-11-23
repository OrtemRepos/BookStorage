from typing import Any

from src.core.ports.database.database import DatabaseInterface
from src.core.ports.database.operation import Operation


class WriteAheadLogInterface:
    def write_log[OperationType: Operation](self, operation: OperationType):
        pass

    def read_log(self) -> list[dict[str, Any]]:
        pass

    def undo_transaction(self, database: DatabaseInterface, tid: int):
        pass

    def clear_log(self):
        pass

    def apply_log(self, database: DatabaseInterface):
        pass
