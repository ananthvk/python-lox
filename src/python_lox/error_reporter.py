from typing import Literal, List, Tuple
from .token import Token

ErrorLevel = Literal["warn", "error", "fatal"]

MAX_ERRORS = 100


class ErrorReporter:
    def __init__(self) -> None:
        # Is there an active error
        self.is_error = False
        self.messages: List[Tuple[ErrorLevel, str, Token | None]] = []

    def report(self, level: ErrorLevel, message: str, token: Token | None = None) -> None:
        self.messages.append((level, message, token))
        self.is_error = True

    def too_many_errors(self) -> bool:
        return len(self.messages) > MAX_ERRORS

    def get_token_line(self, src: str, token: Token) -> Tuple[str, int, int]:
        """
        Returns the line of which the token is part of, along with the start of line, and end of line + 1
        """
        if token.start == 0 and token.end == 0:
            return "", 0, 0

        # Traverse left until we hit a newline
        i = token.start
        while i >= 0 and src[i] != "\n":
            i -= 1

        # Traverse right until we hit a newline
        j = token.end
        while j < len(src) and src[j] != "\n":
            j += 1

        return src[i + 1 : j], i + 1, j
