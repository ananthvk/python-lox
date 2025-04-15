from typing import Literal, List, Tuple
from .token import Token

ErrorLevel = Literal["warn", "error", "fatal"]

MAX_ERRORS = 100


class ErrorReporter:
    def __init__(self) -> None:
        # Is there an active error
        self.is_error = False
        self.messages: List[Tuple[ErrorLevel, str]] = []

    def report(self, level: ErrorLevel, message: str, token: Token | None = None):
        self.messages.append((level, message))
        self.is_error = True

    def too_many_errors(self) -> bool:
        return len(self.messages) > MAX_ERRORS
