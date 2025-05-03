from typing import TYPE_CHECKING, Dict, List, override

from .exceptions import RuntimeException
from .token import Token

if TYPE_CHECKING:
    from python_lox.interpreter import Interpreter
from .callable import Callable, LoxFunction


class LoxClass(Callable):
    def __init__(self, name_: str, methods: Dict[str, LoxFunction]) -> None:
        super().__init__()
        self.name_ = name_
        self.methods = methods

    def __str__(self) -> str:
        return f"<class {self.name_}>"

    @override
    def name(self) -> str:
        return self.name_

    @override
    def arity(self) -> int:
        return 0

    @override
    def call(self, interpreter: "Interpreter", args: List[object]) -> object:
        instance = LoxInstance(class_=self)
        return instance


class LoxInstance:
    def __init__(self, class_: LoxClass) -> None:
        self.class_ = class_
        self.fields: Dict[str, object] = {}

    def __str__(self) -> str:
        return f"<{self.class_.name()} instance at 0x{id(self):x}>"

    def get(self, name: Token) -> object:
        value = self.fields.get(name.string_repr)
        if value is not None:
            return value

        value = self.class_.methods.get(name.string_repr)
        if value is not None:
            return value.bind(self)

        raise RuntimeException(
            f'Error: There is no attribute "{name.string_repr}" on an instance of class "{self.class_.name()}"',
            token=name,
        )

    def set(self, name: Token, value: object) -> None:
        self.fields[name.string_repr] = value
