from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class BookStatus(StrEnum):
    IN_STOCK = "in_stock"
    ISSUED = "issued"


@dataclass
class Book:
    def __init__(self, id: int, title: str, author: str, year: int, status: BookStatus):
        self.id = id
        self.title = title
        self.author = author
        self.year = year
        self._status = status

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status: BookStatus):
        if self._status == BookStatus.ISSUED or status == BookStatus.IN_STOCK:
            self._status = status
        else:
            raise ValueError(
                f"Invalid status: {status}. Expected: {BookStatus.ISSUED}"
                "or {BookStatus.IN_STOCK}"
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            id=data["id"],
            title=data["title"],
            author=data["author"],
            year=data["year"],
            status=data["status"],
        )
