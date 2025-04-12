from typing import List
from .token import Token, TokenType


class Lexer:
    def __init__(self, source: str):
        self.source = source
        # Index of the first character of the current token
        self.index = 0
        # Current character to be considered
        self.current = 0
        # Line number
        self.line = 0

    def advance(self) -> str:
        if self.current < len(self.source):
            ch =  self.source[self.current]
            self.current += 1
            return ch
        return "\0"

    def create_token(self, token_type: TokenType) -> Token:
        token = Token()
        token.string_repr = self.source[self.index : self.current]
        token.token_type = token_type
        token.line = self.line
        return token

    def find_token(self) -> Token:
        character = self.advance()
        token: Token = Token()
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
            case _:
                pass
        return token

    def process(self) -> List[Token]:
        tokens: List[Token] = []

        while self.current < len(self.source):
            self.index = self.current
            tokens.append(self.find_token())

        # Add an EOF token, so that parsing becomes easier
        tokens.append(Token(token_type=TokenType.EOF))
        return tokens
