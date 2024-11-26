from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class BookStatus(StrEnum):
    IN_STOCK = "in_stock"
    ISSUED = "issued"


@dataclass
class Book:
    id: int
    title: str
    author: str
    year: int
    enum_status: BookStatus

    @property
    def status(self):
        return self.enum_status

    @status.setter
    def status(self, value: BookStatus):
        if value == BookStatus.ISSUED or value == BookStatus.IN_STOCK:
            self.enum_status = value
        else:
            raise ValueError(
                f"Invalid status: {value}. Expected: {BookStatus.ISSUED}"
                f"or {BookStatus.IN_STOCK}"
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
            enum_status=data["status"],
        )
