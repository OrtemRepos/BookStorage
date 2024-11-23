import json
from pathlib import Path
from typing import Any

from core.ports.database.database import DatabaseInterface
from src.core.ports.database.wal import Operation, WriteAheadLogInterface
from src.infrastructure.database.operation import OperationFactory

type LogList = dict[int, dict[int, dict[str, Any]]]


class WriteAheadLog(WriteAheadLogInterface):
    def __init__(self, log_filepath: str):
        self.log_filepath = log_filepath
        self._log, self._last_processed_tid = self._from_file()

    def _save_log(self):
        with open(self.log_filepath, "w") as f:
            json.dump(
                {
                    "log": self._log,
                },
                f,
            )

    def _from_file(self) -> tuple[LogList, int]:
        if not Path(self.log_filepath).exists():
            return {}, 0
        try:
            with open(self.log_filepath) as f:
                data = json.load(f)
                return data["log"], data["tid"]
        except Exception as e:
            print("Error reading log file:", e)
            return {}, 0

    def write_log[OperationType: Operation](self, tid: int, operation: OperationType):
        if self._log.get(tid) is None:
            self._log[tid] = []
        self._log[tid].append(operation.to_dict())
        self._save_log()

    def get_log(self):
        return self._log

    def clear_log(self):
        self._log = []
        self._last_processed_lsn = 0
        self._save_log()

    def undo_last_transaction(self, database: DatabaseInterface):
        last_tid = self._last_processed_tid

        try:
            for lsn in self._log[last_tid]:
                operation = OperationFactory.create(
                    lsn,
                    self._log[last_tid][lsn]["operation"],
                    database,
                    self._log[last_tid][lsn],
                )
                operation.undo()
            del self._log[last_tid]
            self._save_log()
        except Exception as e:
            print("Error during undo of last transaction", e)

    def apply_log(self, database: DatabaseInterface):
        from_index = sorted(self._log.keys(), reverse=True)[self._last_processed_tid :]
        for tid in from_index:
            for lsn in sorted(list(self._log[tid].keys())):
                operation = OperationFactory.create(
                    lsn,
                    self._log[tid][lsn]["operation"],
                    database,
                    self._log[tid][lsn],
                )
                operation.execute()
            self._last_processed_tid = tid
