from typing import Dict, Tuple, Literal, Set
from .token import Token

EnvironmentValueType = Tuple[Literal["uninitialized", "initialized"], object]


class NameException(Exception):
    def __init__(self, message: str, token: Token) -> None:
        super().__init__(message)
        self.token = token


class Environment:
    def __init__(self, parent: "Environment | None" = None) -> None:
        self.parent: Environment | None = parent
        self.values: Dict[str, EnvironmentValueType] = {}
        self.const_variables: Set[str] = set()

    def assign(self, token: Token, value: object) -> None:
        if token.string_repr in self.const_variables:
            raise NameException(
                f'Type Error: Assignment not permitted since "{token.string_repr}" is declared const',
                token,
            )

        v = self.values.get(token.string_repr)
        if v is not None:
            self.values[token.string_repr] = ("initialized", value)
            return

        if self.parent is not None:
            self.parent.assign(token, value)
            return

        raise NameException(f'Name Error: "{token.string_repr}" is not defined', token)

    def declare(
        self,
        token: Token,
        val: object | None = None,
        initialize: bool = False,
        const: bool = False,
    ) -> None:
        value = self.values.get(token.string_repr)
        if value is not None:
            raise NameException(
                f'Name Error: "{token.string_repr}" has already been declared', token
            )

        if initialize:
            self.values[token.string_repr] = ("initialized", val)
        else:
            self.values[token.string_repr] = ("uninitialized", None)
        if const:
            self.const_variables.add(token.string_repr)

    def get(self, token: Token) -> object:
        value = self.values.get(token.string_repr)
        if value is not None:
            if value[0] == "uninitialized":
                raise NameException(
                    f'Value Error: "{token.string_repr}" is not initialized', token
                )

            return value[1]

        if self.parent is not None:
            return self.parent.get(token)

        raise NameException(f'Name Error: "{token.string_repr}" is not defined', token)
