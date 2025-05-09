from typing import TYPE_CHECKING, Dict, List, override

from .exceptions import RuntimeException
from .token import Token

if TYPE_CHECKING:
    from python_lox.interpreter import Interpreter
from .callable import Callable, LoxFunction


class LoxInstance:
    def __init__(
        self, class_: "LoxClass", base_class_instance: "LoxInstance | None" = None
    ) -> None:
        self.class_ = class_
        self.fields: Dict[str, object] = {}
        self.base_class_instance: LoxInstance | None = base_class_instance

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

        if self.base_class_instance is not None:
            try:
                return self.base_class_instance.get(name, interpreter)
            except RuntimeException as r:
                if str(r).startswith("Error: There is no attribute"):
                    raise RuntimeException(
                        f'Error: There is no attribute "{name.string_repr}" on an instance of class "{self.class_.name()}"',
                        token=name,
                    )
                else:
                    raise r

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
        base_class: "LoxClass | None" = None,
    ) -> None:
        LoxInstance.__init__(self, Meta())
        Callable.__init__(self)
        self.name_ = name_
        self.methods = methods
        self.getters = getters
        self.base_class = base_class

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
    def call(
        self,
        interpreter: "Interpreter",
        args: List[object],
        do_not_call_init: bool = False,
    ) -> object:
        base_class_instance: LoxInstance | None = None
        if self.base_class:
            base_class_instance = self.base_class.call(interpreter, [], True)  # type: ignore

        instance = LoxInstance(class_=self, base_class_instance=base_class_instance)
        if not do_not_call_init:
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
        self.base_class = None

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
    def call(
        self,
        interpreter: "Interpreter",
        args: List[object],
        do_not_call_init: bool = False,
    ) -> object:
        instance = LoxInstance(class_=self)
        if not do_not_call_init:
            constructor = self.methods.get("init")
            if constructor is not None:
                constructor.bind(instance).call(interpreter, args)
        return instance
