import json
from pathlib import Path
from typing import Any

from src.core.ports.database.database import (
    DatabaseInterface,
    TransactionInterface,
    WriteAheadLogInterface,
)
from src.infrastructure.database.transaction import TransactionFactory
from src.infrastructure.util import convert_keys_to_int

type LogDict = dict[int, dict[int, dict[str, Any]]]


class SimpleWAL(WriteAheadLogInterface):
    def __init__(self):
        self._log: list[TransactionInterface] = []

    def write_log[TransactionType: TransactionInterface](self, transaction: TransactionType):
        self._log.append(transaction)

    def get_log(self) -> LogDict:
        return self._log

    def clear_log(self):
        self._log = {}

    def apply_log(self, database: DatabaseInterface):
        for transaction in self._log:
            transaction.commit(with_wal=False)


class WriteAheadLog(WriteAheadLogInterface):
    def __init__(self, log_filepath: str):
        self.log_filepath = Path(log_filepath)
        self._log = self._from_file()

    def _save_log(self):
        with open(self.log_filepath, "w") as f:
            json.dump(self._log, f)


    def _from_file(self) -> LogDict:
        if not Path(self.log_filepath).exists():
            return {}
        try:
            log = {}
            with open(self.log_filepath) as f:
                data = json.load(f)
                log = data
                log = convert_keys_to_int(log)
                return log
        except Exception as e:
            raise FileNotFoundError("Error reading log file\nTraceback:\n\t", e) from e

    def write_log[TransactionType: TransactionInterface](self, transaction: TransactionType):
        self._log.update(transaction.to_dict())
        self._save_log()

    def get_log(self) -> LogDict:
        return self._log

    def clear_log(self):
        self._log = {}
        self._save_log()

    def apply_log(self, database: DatabaseInterface):
        from_index = sorted(self._log.keys())
        for tid in from_index:
            transaction_dict = self._log[tid]
            transaction = TransactionFactory.create(tid, database, transaction_dict)
            transaction.commit(with_wal=False)
