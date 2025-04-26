from typing import List

from .exceptions import LexerException
from .token import Token, TokenType
from .token import keywords, double_char_tokens, single_char_tokens
from .error_reporter import ErrorReporter


class Lexer:
    def __init__(self, source: str, error_reporter: ErrorReporter | None = None):
        self.source = source
        # Index of the first character of the current token
        self.index = 0
        # Current character to be consumed
        # Note: self.current has not yet been consumed, i.e. it's the next character
        self.current = 0
        # Line number
        self.line = 1

        self.error_reporter = error_reporter

    def advance(self) -> str:
        if self.current < len(self.source):
            ch = self.source[self.current]
            self.current += 1
            return ch
        return "\0"

    def match(self, character: str) -> bool:
        """
        Returns true and increments current, if source[current] is the required character
        Otherwise returns false
        """
        # There are no more characters to lex
        if self.current >= len(self.source):
            return False

        if self.source[self.current] == character:
            self.current += 1
            return True

        return False

    def lookahead(self) -> str:
        if self.current >= len(self.source):
            return "\0"
        return self.source[self.current]

    def lookahead2(self) -> str:
        if (self.current + 1) >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def create_token(self, token_type: TokenType) -> Token:
        token = Token()
        token.string_repr = self.source[self.index : self.current]
        token.token_type = token_type
        token.line = self.line
        token.start = self.index
        token.end = self.current
        return token

    def find_string(self) -> Token:
        # Note: Strings are multiline by default

        # Find the terminating "
        while self.lookahead() != '"' and self.current < len(self.source):
            if self.lookahead() == "\n":
                self.line += 1
            self.advance()

        # We have reached end of file
        if self.current >= len(self.source):
            raise LexerException(
                "Syntax Error: Unterminated string literal",
                self.line,
                self.index,
                self.current,
            )

        # Consume the closing string literal
        self.advance()

        token = self.create_token(TokenType.STRING)
        # Literal value, without starting and closing quotes
        token.literal = self.source[self.index + 1 : self.current - 1]
        return token

    def find_hex_number(self) -> Token:
        valid_chars = ["a", "b", "c", "d", "e", "f"]
        while self.lookahead().isdigit() or self.lookahead().lower() in valid_chars:
            self.advance()

        if (
            self.lookahead().isalpha()
            or self.lookahead() == "_"
            or self.lookahead() == "."
        ):
            raise LexerException(
                f"Syntax Error: Invalid character in hexadecimal literal '{self.lookahead()}' ",
                self.line,
                self.index,
                self.current,
            )
        lexeme = self.source[self.index : self.current]
        if lexeme.endswith("x") or lexeme.endswith("X"):
            raise LexerException(
                f"Syntax Error: Incomplete hexadecimal literal 0x",
                self.line,
                self.index,
                self.current,
            )

        token = self.create_token(TokenType.NUMBER)
        token.literal = int(lexeme, base=16)
        return token

    def find_binary_number(self) -> Token:
        valid_chars = ["0", "1"]
        while self.lookahead() in valid_chars:
            self.advance()

        if (
            self.lookahead().isalnum()
            or self.lookahead() == "_"
            or self.lookahead() == "."
        ):
            raise LexerException(
                f"Syntax Error: Invalid character in binary literal '{self.lookahead()}' ",
                self.line,
                self.index,
                self.current,
            )
        lexeme = self.source[self.index : self.current]
        if lexeme.endswith("b") or lexeme.endswith("B"):
            raise LexerException(
                f"Syntax Error: Incomplete binary literal 0b",
                self.line,
                self.index,
                self.current,
            )

        token = self.create_token(TokenType.NUMBER)
        token.literal = int(lexeme, base=2)
        return token

    def find_octal_number(self) -> Token:
        valid_chars = ["0", "1", "2", "3", "4", "5", "6", "7"]
        while self.lookahead() in valid_chars:
            self.advance()

        if (
            self.lookahead().isalnum()
            or self.lookahead() == "_"
            or self.lookahead() == "."
        ):
            raise LexerException(
                f"Syntax Error: Invalid character in octal literal '{self.lookahead()}' ",
                self.line,
                self.index,
                self.current,
            )
        lexeme = self.source[self.index : self.current]
        if lexeme.endswith("o") or lexeme.endswith("O"):
            raise LexerException(
                f"Syntax Error: Incomplete octal literal 0o",
                self.line,
                self.index,
                self.current,
            )

        token = self.create_token(TokenType.NUMBER)
        token.literal = int(lexeme, base=8)
        return token

    def find_number(self, ch: str) -> Token:
        """
        Args:
            ch: The matched character, i.e. the first character of the numeric string
        """
        if ch == "0":
            if self.match("x") or self.match("X"):
                return self.find_hex_number()
            if self.match("b") or self.match("B"):
                return self.find_binary_number()
            if self.match("o") or self.match("O"):
                return self.find_octal_number()

        # While the next character is a digit, move forward
        while self.lookahead().isdigit():
            self.advance()

        # Check for an optional ., followed by digits
        if self.lookahead() == "." and self.lookahead2().isdigit():
            self.advance()

        while self.lookahead().isdigit():
            self.advance()

        # Look for an optional 'e', for exponent part
        if self.lookahead() == "e" or self.lookahead() == "E":
            self.advance()
            # Look for an optional sign (+ / -)
            if self.lookahead() == "+" or self.lookahead() == "-":
                self.advance()

            # There should be atleast one digit
            if not self.lookahead().isdigit():
                raise LexerException(
                    "Syntax Error: Invalid numeric literal, no number following 'e'",
                    self.line,
                    self.index,
                    self.current,
                )

            # Consume remaining digits
            while self.lookahead().isdigit():
                self.advance()

        if (
            self.lookahead().isalpha()
            or self.lookahead() == "_"
            or self.lookahead() == "."
        ):
            raise LexerException(
                f"Syntax Error: Invalid character in decimal literal '{self.lookahead()}' ",
                self.line,
                self.index,
                self.current,
            )

        token = self.create_token(TokenType.NUMBER)
        literal = self.source[self.index : self.current]
        try:
            token.literal = int(literal)
        except:
            token.literal = float(literal)
        return token

    def find_block_comment(self) -> None:
        while not (
            self.lookahead() == "*" and self.lookahead2() == "/"
        ) and self.current < len(self.source):
            if self.lookahead() == "\n":
                self.line += 1
            self.advance()

        # If we have reached the end of source program without finding the closing comment
        if self.current >= len(self.source):
            raise LexerException(
                "Syntax Error: Unterminated block comment",
                self.line,
                self.index,
                self.current,
            )

        self.advance()
        self.advance()

    def find_identifier(self) -> Token:
        while self.lookahead().isalnum() or self.lookahead() == "_":
            self.advance()

        token = self.create_token(TokenType.IDENTIFIER)
        token.literal = self.source[self.index : self.current]

        keyword = keywords.get(token.literal)
        if keyword is not None:
            token.token_type = keyword
            token.literal = None

        return token

    def find_token(self) -> Token | None:
        """
        Returns the next token, or None if there are no more tokens
        """
        character = self.advance()

        for token_str in double_char_tokens:
            if character == token_str[0] and self.match(token_str[1]):
                return self.create_token(double_char_tokens[token_str])

        for token_str in single_char_tokens:
            if character == token_str[0]:
                return self.create_token(single_char_tokens[token_str])

        match character:
            case " " | "\t" | "\r":
                pass

            case "\n":
                self.line += 1

            case "/":
                if self.match("/"):
                    # A single line comment was found, skip until the end of line (but do not consume the newline)
                    while self.lookahead() != "\n" and self.current < len(self.source):
                        self.advance()
                elif self.match("*"):
                    self.find_block_comment()
                else:
                    return self.create_token(TokenType.SLASH)

            case '"':
                return self.find_string()

            case _:
                if character.isdigit():
                    # It may be a number
                    return self.find_number(character)
                elif character.isalpha() or character == "_":
                    # It may be an identifier
                    return self.find_identifier()
                else:
                    raise LexerException(
                        f"Syntax Error: Invalid character '{character}'",
                        self.line,
                        self.index,
                        self.current,
                    )
        return None

    def process(self) -> List[Token]:
        tokens: List[Token] = []

        while self.current < len(self.source):
            self.index = self.current
            try:
                token = self.find_token()
                if token is None:
                    continue
                tokens.append(token)
            except LexerException as e:
                if self.error_reporter is None:
                    raise e
                self.error_reporter.report("error", f"{str(e)} at line {e.line_no}")
                while self.current < len(self.source):
                    if (
                        self.lookahead() == "\n"
                        or self.lookahead() == "{"
                        or self.lookahead() == "}"
                    ):
                        break
                    self.advance()

        # Add an EOF token, so that parsing becomes easier
        tokens.append(Token(token_type=TokenType.EOF))
        return tokens
