from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    # Separators
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    SEMICOLON = auto()

    # Arithmetic operators
    MINUS = auto()
    PLUS = auto()
    SLASH = auto()
    STAR = auto()

    # Relational operators
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords
    AND = auto()
    OR = auto()
    # Extra: Add not keyword
    NOT = auto()

    FALSE = auto()
    TRUE = auto()
    NIL = auto()

    IF = auto()
    ELSE = auto()

    CLASS = auto()
    FUN = auto()

    FOR = auto()
    WHILE = auto()

    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    VAR = auto()
    EOF = auto()
    
    UNKNOWN = auto()


@dataclass
class Token:
    token_type: TokenType = TokenType.UNKNOWN
    line: int = 0
    literal: int | float | str | None = None
    string_repr: str = ""
    
    def __repr__(self) -> str:
        if self.token_type in [TokenType.IDENTIFIER, TokenType.STRING, TokenType.NUMBER]:
            return f'<{self.token_type} {self.literal}>'
        return f'<{self.token_type}>'
