from typing import Dict

from .token import Token


class Environment:
    class UNSET:
        pass

    def __init__(self, parent: "Environment | None" = None) -> None:
        self.parent: Environment | None = parent
        self.values: Dict[str, object] = {}

    def is_declared(self, name: Token | str) -> bool:
        """
        Returns true if "name" is declared in the current scope
        Note: This method does not check all preceding environments, only the current one
        """
        if isinstance(name, Token):
            return name.string_repr in self.values
        return name in self.values

    def assign(self, token: Token, value: object) -> None:
        if self.is_declared(token):
            self.values[token.string_repr] = value
        elif self.parent is not None:
            self.parent.assign(token, value)
        else:
            raise ValueError("Logic Error: This should not be thrown")

    def declare(self, token: Token | str) -> None:
        if isinstance(token, Token):
            self.values[token.string_repr] = None
        else:
            self.values[token] = None

    def define(self, token: Token | str, value: object) -> None:
        if isinstance(token, Token):
            self.values[token.string_repr] = value
        else:
            self.values[token] = value

    def get(self, token: Token) -> object:
        v = self.values.get(token.string_repr)
        if v is not None:
            return v
        elif self.parent is not None:
            return self.parent.get(token)
        return None

    def ancestor(self, nesting: int) -> "Environment":
        environment: Environment = self
        for _ in range(nesting):
            if not environment.parent:
                break
            environment = environment.parent
        return environment

    def get_at(self, nesting: int, token: Token) -> object:
        return self.ancestor(nesting).get(token)

    def assign_at(self, nesting: int, token: Token, value: object) -> None:
        self.ancestor(nesting).assign(token, value)
