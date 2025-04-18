
from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    AND = auto()
    ASSERT = auto()
    BANG = auto()
    BANG_EQUAL = auto()
    BREAK = auto()
    CLASS = auto()
    COLON = auto()
    COMMA = auto()
    CONST = auto()
    CONTINUE = auto()
    DOT = auto()
    ELSE = auto()
    EOF = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    FALSE = auto()
    FOR = auto()
    FUN = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    IDENTIFIER = auto()
    IF = auto()
    LEFT_BRACE = auto()
    LEFT_PAREN = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    MINUS = auto()
    NIL = auto()
    NOT = auto()
    NUMBER = auto()
    OR = auto()
    PERCENTAGE = auto()
    PLUS = auto()
    PRINT = auto()
    QUESTION_MARK = auto()
    RETURN = auto()
    RIGHT_BRACE = auto()
    RIGHT_PAREN = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()
    STRING = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    TYPEOF = auto()
    UNKNOWN = auto()
    VAR = auto()
    WHILE = auto()

keywords = {
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "false": TokenType.FALSE,
    "nil": TokenType.NIL,
    "true": TokenType.TRUE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "class": TokenType.CLASS,
    "fun": TokenType.FUN,
    "for": TokenType.FOR,
    "while": TokenType.WHILE,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "var": TokenType.VAR,
    "const": TokenType.CONST,
    "typeof": TokenType.TYPEOF,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "assert": TokenType.ASSERT,
}

single_char_tokens = {
    "(": TokenType.LEFT_PAREN,
    ")": TokenType.RIGHT_PAREN,
    "{": TokenType.LEFT_BRACE,
    "}": TokenType.RIGHT_BRACE,
    ",": TokenType.COMMA,
    ".": TokenType.DOT,
    "-": TokenType.MINUS,
    "+": TokenType.PLUS,
    ";": TokenType.SEMICOLON,
    "*": TokenType.STAR,
    "!": TokenType.BANG,
    ">": TokenType.GREATER,
    "<": TokenType.LESS,
    "=": TokenType.EQUAL,
    ":": TokenType.COLON,
    "?": TokenType.QUESTION_MARK,
    "%": TokenType.PERCENTAGE,
}

double_char_tokens = {
    "!=": TokenType.BANG_EQUAL,
    ">=": TokenType.GREATER_EQUAL,
    "<=": TokenType.LESS_EQUAL,
    "==": TokenType.EQUAL_EQUAL,
}

misc = {
    "identifier": TokenType.IDENTIFIER,
    "number": TokenType.NUMBER,
    "eof": TokenType.EOF,
    "unknown": TokenType.UNKNOWN,
    "string": TokenType.STRING,
    "slash": TokenType.SLASH,
}

@dataclass
class Token:
    token_type: TokenType = TokenType.UNKNOWN
    line: int = 0
    literal: int | float | str | None = None
    string_repr: str = ""
    start: int = 0
    end: int = 0

    def __repr__(self) -> str:
        if self.token_type == TokenType.IDENTIFIER:
            return f"<{self.token_type} {self.literal}>"
        elif self.token_type == TokenType.STRING:
            return f'<{self.token_type} "{self.literal}">'
        elif self.token_type == TokenType.NUMBER:
            if (
                isinstance(self.literal, float) or isinstance(self.literal, int)
            ):
                return f"<{self.token_type} {self.literal}>"

        return f"<{self.token_type}>"
