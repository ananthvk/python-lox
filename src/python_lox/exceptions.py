from .ast import expr as Expr
from .token import Token


class ParserException(Exception):
    def __init__(self, message: str, token: Token) -> None:
        super().__init__(message)
        self.token = token


class LexerException(Exception):
    def __init__(self, message: str, line_no: int, index: int, current: int) -> None:
        super().__init__(message)
        self.line_no = line_no
        # Exception occured when lexing token from [index, current)
        self.index = index
        self.current = current


class RuntimeException(Exception):
    def __init__(
        self, message: str, exp: Expr.Expr | None = None, token: Token | None = None
    ) -> None:
        super().__init__(message)
        self.exp = exp
        self.token = token


class ContinueException(Exception):
    pass


class BreakException(Exception):
    pass


class ReturnException(Exception):
    def __init__(self, value: object | None = None) -> None:
        super().__init__()
        self.value = value


class NameException(Exception):
    def __init__(self, message: str, token: Token) -> None:
        super().__init__(message)
        self.token = token
