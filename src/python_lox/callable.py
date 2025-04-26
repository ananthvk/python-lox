from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .interpreter import Interpreter


class Callable(ABC):
    @abstractmethod
    def arity(self) -> int:
        pass

    @abstractmethod
    def call(self, interpreter: "Interpreter", args: List[object]) -> object:
        pass

    @abstractmethod
    def name(self) -> str:
        pass
