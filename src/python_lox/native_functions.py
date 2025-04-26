import time
from .callable import Callable
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .interpreter import Interpreter


class Clock(Callable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", args: List[object]) -> object:
        return time.time()

    def name(self):
        return "clock"

    def __str__(self) -> str:
        return "<native function clock>"


native_functions = [Clock()]
