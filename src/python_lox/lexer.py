from typing import List
from .token import Token, TokenType


class LexerException(Exception):
    def __init__(self, message: str, line_no: int, index: int, current: int) -> None:
        super().__init__(message)
        self.line_no = line_no
        # Exception occured when lexing token from [index, current)
        self.index = index
        self.current = current


class Lexer:
    def __init__(self, source: str):
        self.source = source
        # Index of the first character of the current token
        self.index = 0
        # Current character to be consumed
        # Note: self.current has not yet been consumed, i.e. it's the next character
        self.current = 0
        # Line number
        self.line = 1

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

    def create_token(self, token_type: TokenType) -> Token:
        token = Token()
        token.string_repr = self.source[self.index : self.current]
        token.token_type = token_type
        token.line = self.line
        return token

    def find_token(self) -> Token | None:
        """
        Returns the next token, or None if there are no more tokens
        """
        character = self.advance()
        token: Token | None = None

        match character:
            case "(":
                token = self.create_token(TokenType.LEFT_PAREN)
            case ")":
                token = self.create_token(TokenType.RIGHT_PAREN)
            case "{":
                token = self.create_token(TokenType.LEFT_BRACE)
            case "}":
                token = self.create_token(TokenType.RIGHT_BRACE)
            case ",":
                token = self.create_token(TokenType.COMMA)
            case ".":
                token = self.create_token(TokenType.DOT)
            case "-":
                token = self.create_token(TokenType.MINUS)
            case "+":
                token = self.create_token(TokenType.PLUS)
            case ";":
                token = self.create_token(TokenType.SEMICOLON)
            case "*":
                token = self.create_token(TokenType.STAR)

            case "!":
                if self.match("="):
                    token = self.create_token(TokenType.BANG_EQUAL)
                else:
                    token = self.create_token(TokenType.BANG)
            case ">":
                if self.match("="):
                    token = self.create_token(TokenType.GREATER_EQUAL)
                else:
                    token = self.create_token(TokenType.GREATER)
            case "<":
                if self.match("="):
                    token = self.create_token(TokenType.LESS_EQUAL)
                else:
                    token = self.create_token(TokenType.LESS)
            case "=":
                if self.match("="):
                    token = self.create_token(TokenType.EQUAL_EQUAL)
                else:
                    token = self.create_token(TokenType.EQUAL)

            case " " | "\t" | "\r":
                pass

            case "\n":
                self.line += 1

            case "/":
                if self.match("/"):
                    # A single line comment was found, skip until the end of line (but do not consume the newline)
                    while self.lookahead() != "\n" and self.current < len(self.source):
                        self.advance()
                else:
                    token = self.create_token(TokenType.SLASH)

            case _:
                raise LexerException(
                    f"Invalid character '{character}'",
                    self.line,
                    self.index,
                    self.current,
                )
        return token

    def process(self) -> List[Token]:
        tokens: List[Token] = []

        while self.current < len(self.source):
            self.index = self.current
            token = self.find_token()
            if token is None:
                continue
            tokens.append(token)

        # Add an EOF token, so that parsing becomes easier
        tokens.append(Token(token_type=TokenType.EOF))
        return tokens
