from typing import List
from .token import Token, TokenType

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
}


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

    def lookahead2(self) -> str:
        if (self.current + 1) >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def create_token(self, token_type: TokenType) -> Token:
        token = Token()
        token.string_repr = self.source[self.index : self.current]
        token.token_type = token_type
        token.line = self.line
        return token

    def find_string(self):
        # Note: Strings are multiline by default

        # Find the terminating "
        while self.lookahead() != '"' and self.current < len(self.source):
            if self.lookahead() == "\n":
                self.line += 1
            self.advance()

        # We have reached end of file
        if self.current >= len(self.source):
            raise LexerException(
                "Unterminated string literal", self.line, self.index, self.current
            )

        # Consume the closing string literal
        self.advance()

        token = self.create_token(TokenType.STRING)
        # Literal value, without starting and closing quotes
        token.literal = self.source[self.index + 1 : self.current - 1]
        return token

    def find_number(self):
        # While the next character is a digit, move forward
        while self.lookahead().isdigit():
            self.advance()

        # Check for an optional ., followed by digits
        if self.lookahead() == "." and self.lookahead2().isdigit():
            self.advance()

        while self.lookahead().isdigit():
            self.advance()

        if self.lookahead().isalpha() or self.lookahead() == "_":
            raise LexerException(
                f"Invalid character in numeric literal '{self.lookahead()}' ",
                self.line,
                self.index,
                self.current,
            )

        token = self.create_token(TokenType.NUMBER)
        token.literal = float(self.source[self.index : self.current])
        return token

    def find_identifier(self):
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

            case '"':
                token = self.find_string()

            case _:
                if character.isdigit():
                    # It may be a number
                    token = self.find_number()
                elif character.isalpha() or character == "_":
                    # It may be an identifier
                    token = self.find_identifier()
                else:
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
