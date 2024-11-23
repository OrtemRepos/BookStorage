from abc import ABC, abstractmethod


class Operation(ABC):
    tid: int

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

    @abstractmethod
    def to_dict(self):
        pass
