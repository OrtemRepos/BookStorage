from typing import Protocol

from src.core.ports.database.transaction import TransactionInterface
from src.core.ports.database.wal import WriteAheadLogInterface


class DatabaseInterface(Protocol):
    wal: WriteAheadLogInterface
    data: dict[int, object]

    def set[ValueType: object](self, key: int, value: ValueType):
        pass

    def delete(self, key: int):
        pass

    def get[ValueType: object](self, key: int) -> ValueType:
        pass

    def get_all[ValueType: object]() -> list[ValueType]:
        pass

    def begin_transaction[TransactionType: TransactionInterface](
        self,
    ) -> TransactionType:
        pass
