import time
import math
from .callable import Callable
from .exceptions import RuntimeException
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .interpreter import Interpreter


class Clock(Callable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", args: List[object]) -> object:
        return time.time()

    def name(self) -> str:
        return "clock"

    def __str__(self) -> str:
        return "<native function clock>"


class Input(Callable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", args: List[object]) -> object:
        return input()

    def name(self) -> str:
        return "input"

    def __str__(self) -> str:
        return "<native function input>"


class Len(Callable):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", args: List[object]) -> object:
        if not isinstance(args[0], str):
            raise RuntimeException(
                "Runtime Exception: len function only works with str"
            )
        return len(args[0])

    def name(self) -> str:
        return "len"

    def __str__(self) -> str:
        return "<native function len>"


class Floor(Callable):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", args: List[object]) -> object:
        if not (isinstance(args[0], int) or isinstance(args[0], float)):
            raise RuntimeException(
                "Runtime Exception: floor function only works with numeric values"
            )
        return math.floor(args[0])

    def name(self) -> str:
        return "floor"

    def __str__(self) -> str:
        return "<native function floor>"


native_functions: List[Callable] = [Clock(), Input(), Len(), Floor()]
