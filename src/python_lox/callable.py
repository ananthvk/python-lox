from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING, Final, override
from .ast import stmt
from .environment import Environment

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


class LoxFunction(Callable):
    def __init__(self, declaration: stmt.Function) -> None:
        self.declaration: Final[stmt.Function] = declaration

    @override
    def name(self) -> str:
        return self.declaration.name.string_repr

    def __str__(self) -> str:
        return f"<function {self.name()}>"

    @override
    def arity(self) -> int:
        return len(self.declaration.params)

    @override
    def call(self, interpreter: "Interpreter", args: List[object]) -> object:
        environment = Environment(parent=interpreter.globals)
        for i in range(len(args)):
            environment.declare(
                self.declaration.params[i], val=args[i], initialize=True
            )

        interpreter.execute_multiple_statements(self.declaration.body, environment)
        return None
