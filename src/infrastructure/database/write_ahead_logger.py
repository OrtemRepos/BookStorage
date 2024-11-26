import json
from pathlib import Path
from typing import Any

from src.core.ports.database.database import (
    DatabaseInterface,
    TransactionInterface,
    WriteAheadLogInterface,
)
from src.infrastructure.database.transaction import TransactionFactory

type LogDict = dict[int, dict[int, dict[str, Any]]]


class SimpleWAL(WriteAheadLogInterface):
    def __init__(self):
        self._log = []
        self._last_processed_tid = None

    def write_log[TransactionType: TransactionInterface](self, transaction: TransactionType):
        self._log.append(transaction)

    def get_log(self) -> LogDict:
        return self._log

    def clear_log(self):
        self._log = {}

    def apply_log(self):
        for transaction in self._log:
            transaction.commit()


class WriteAheadLog(WriteAheadLogInterface):
    def __init__(self, log_filepath: str):
        self.log_filepath = Path(log_filepath)
        self._log, self._last_processed_tid = self._from_file()

    def _save_log(self):
        with open(self.log_filepath, "w") as f:
            json.dump(
                {"log": self._log, "tid": self._last_processed_tid},
                f,
            )

    @staticmethod
    def _convert_keys_to_int(log: dict) -> dict:
        new_log = {}
        for key, value in log.items():
            try:
                new_key = int(key)
            except Exception:
                new_key = key
            if isinstance(value, dict):
                new_log[new_key] = WriteAheadLog._convert_keys_to_int(value)
            elif isinstance(value, list):
                for i in range(len(value)):
                    value[i] = WriteAheadLog._convert_keys_to_int(value[i])
            else:
                new_log[new_key] = value
        return new_log

    def _from_file(self) -> tuple[LogDict, int | None]:
        if not Path(self.log_filepath).exists():
            return {}, None
        try:
            log = {}
            with open(self.log_filepath) as f:
                data = json.load(f)
                log, last_tid = data["log"], data["tid"]
                log = WriteAheadLog._convert_keys_to_int(log)
                return log, last_tid
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
        from_index = sorted(self._log.keys(), reverse=True)
        if self._last_processed_tid is not None:
            last_processed_tid_index = from_index.index(self._last_processed_tid)
            from_index = from_index[last_processed_tid_index:]
        for tid in from_index:
            transaction_dict = self._log[tid]
            transaction = TransactionFactory.create(tid, database, transaction_dict)
            transaction.commit()
            self._last_processed_tid = tid
