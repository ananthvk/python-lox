from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Final, List, override

from .ast import expr, stmt
from .environment import Environment
from .exceptions import ReturnException
from .token import Token, TokenType

if TYPE_CHECKING:
    from .interpreter import Interpreter
    from .lox_class import LoxInstance


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
    def __init__(
        self,
        declaration: stmt.Function,
        closure: Environment,
        is_initializer: bool = False,
    ) -> None:
        self.declaration: Final[stmt.Function] = declaration
        self.closure: Final[Environment] = closure
        self.is_initializer = is_initializer

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
        environment = Environment(parent=self.closure)
        for i in range(len(args)):
            environment.declare(self.declaration.params[i])
            environment.define(self.declaration.params[i], args[i])
        try:
            interpreter.execute_multiple_statements(self.declaration.body, environment)
        except ReturnException as e:
            if self.is_initializer:
                tok = Token()
                tok.token_type = TokenType.THIS
                tok.string_repr = "this"
                return self.closure.get_at(0, tok)
            return e.value
        if self.is_initializer:
            tok = Token()
            tok.token_type = TokenType.THIS
            tok.string_repr = "this"
            return self.closure.get_at(0, tok)
        return None

    def bind(self, instance: "LoxInstance") -> "LoxFunction":
        environment = Environment(parent=self.closure)
        environment.define("this", instance)
        if instance.base_class_instance is not None:
            environment.define("super", instance.base_class_instance)
        return LoxFunction(
            declaration=self.declaration,
            closure=environment,
            is_initializer=self.is_initializer,
        )


class ArrowFunction(Callable):
    def __init__(self, declaration: expr.Arrow, closure: Environment) -> None:
        self.declaration: Final[expr.Arrow] = declaration
        self.closure: Final[Environment] = closure

    @override
    def name(self) -> str:
        return "<arrow function>"

    def __str__(self) -> str:
        return f"<function {self.name()}>"

    @override
    def arity(self) -> int:
        return len(self.declaration.params)

    @override
    def call(self, interpreter: "Interpreter", args: List[object]) -> object:
        environment = Environment(parent=self.closure)
        for i in range(len(args)):
            environment.declare(self.declaration.params[i])
            environment.define(self.declaration.params[i], args[i])
        try:
            interpreter.execute_multiple_statements(self.declaration.body, environment)
        except ReturnException as e:
            return e.value
        return None
