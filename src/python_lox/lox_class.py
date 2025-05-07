from typing import TYPE_CHECKING, Dict, List, override

from .exceptions import RuntimeException
from .token import Token

if TYPE_CHECKING:
    from python_lox.interpreter import Interpreter
from .callable import Callable, LoxFunction


class LoxInstance:
    def __init__(self, class_: "LoxClass") -> None:
        self.class_ = class_
        self.fields: Dict[str, object] = {}

    def __str__(self) -> str:
        return f"<{self.class_.name()} instance at 0x{id(self):x}>"

    def get(self, name: Token, interpreter: "Interpreter") -> object:
        if name.string_repr in self.fields:
            return self.fields[name.string_repr]

        if name.string_repr in self.class_.getters:
            return (
                self.class_.getters[name.string_repr].bind(self).call(interpreter, [])
            )

        if name.string_repr in self.class_.methods:
            return self.class_.methods[name.string_repr].bind(self)

        if name.string_repr in self.class_.fields:
            return self.class_.fields[name.string_repr]

        if name.string_repr in self.class_.class_.methods:
            return self.class_.class_.methods[name.string_repr]

        raise RuntimeException(
            f'Error: There is no attribute "{name.string_repr}" on an instance of class "{self.class_.name()}"',
            token=name,
        )

    def set(self, name: Token, value: object) -> None:
        self.fields[name.string_repr] = value


class LoxClass(LoxInstance, Callable):
    def __init__(
        self,
        name_: str,
        methods: Dict[str, LoxFunction],
        getters: Dict[str, LoxFunction] = {},
    ) -> None:
        LoxInstance.__init__(self, Meta())
        Callable.__init__(self)
        self.name_ = name_
        self.methods = methods
        self.getters = getters

    def __str__(self) -> str:
        return f"<class {self.name_}>"

    @override
    def name(self) -> str:
        return self.name_

    @override
    def arity(self) -> int:
        constructor = self.methods.get("init")
        if constructor is None:
            return 0
        return constructor.arity()

    @override
    def call(self, interpreter: "Interpreter", args: List[object]) -> object:
        instance = LoxInstance(class_=self)
        constructor = self.methods.get("init")
        if constructor is not None:
            constructor.bind(instance).call(interpreter, args)
        return instance


class Meta(LoxClass):
    def __init__(self) -> None:
        LoxInstance.__init__(self, self)
        Callable.__init__(self)
        self.name_ = "Meta"
        self.methods: Dict[str, LoxFunction] = {}
        self.getters: Dict[str, LoxFunction] = {}

    def __str__(self) -> str:
        return f"<meta {self.name_}>"

    @override
    def name(self) -> str:
        return self.name_

    @override
    def arity(self) -> int:
        constructor = self.methods.get("init")
        if constructor is None:
            return 0
        return constructor.arity()

    @override
    def call(self, interpreter: "Interpreter", args: List[object]) -> object:
        instance = LoxInstance(class_=self)
        constructor = self.methods.get("init")
        if constructor is not None:
            constructor.bind(instance).call(interpreter, args)
        return instance
