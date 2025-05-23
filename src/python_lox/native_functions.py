import math
import time
from typing import TYPE_CHECKING, List

from .callable import Callable
from .exceptions import RuntimeException

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


class ParseInt(Callable):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", args: List[object]) -> object:
        try:
            return int(args[0])  # type: ignore
        except Exception:
            return None

    def name(self) -> str:
        return "parse_int"

    def __str__(self) -> str:
        return "<native function parse_int>"


class ParseFloat(Callable):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", args: List[object]) -> object:
        try:
            return float(args[0])  # type: ignore
        except Exception:
            return None

    def name(self) -> str:
        return "parse_float"

    def __str__(self) -> str:
        return "<native function parse_float>"


class ToString(Callable):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: "Interpreter", args: List[object]) -> object:
        return interpreter.stringify(args[0])

    def name(self) -> str:
        return "to_string"

    def __str__(self) -> str:
        return "<native function to_string>"


"""
Note: ParseInt and ParseFloat works similar to C# try parse, these methods return null if parsing failed, instead of throwing
exception
"""
native_functions: List[Callable] = [
    Clock(),
    Input(),
    Len(),
    Floor(),
    ParseInt(),
    ParseFloat(),
    ToString(),
]
