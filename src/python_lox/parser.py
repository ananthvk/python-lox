from .token import Token, TokenType
from typing import List
from .ast import expr


class ParserException(Exception):
    def __init__(self, message: str, token: Token) -> None:
        super().__init__(message)
        self.token = token


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens

        # Next token to be processed
        self.current = 0

    def match(self, token_types: List[TokenType]) -> bool:
        """
        Checks if the current token type is same as any of the passed token types
        Args:
            token_types: List of token types that needs to be matched
        Returns:
            bool: True if the current token matches any of the passed token type, this method also calls advance(). False otherwise
        """
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def check(self, token_type: TokenType) -> bool:
        """
        Args:
            token_type: Type of token to be checked
        Returns:
            bool: True if the type of the current token is equal to token_type, False otherwise
        """

        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def advance(self) -> Token:
        token = self.tokens[self.current]
        if not self.is_at_end():
            self.current += 1
        return token

    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    # Code for recursive descent parser

    def expression(self) -> expr.Expr:
        return self.equality()

    def equality(self) -> expr.Expr:
        exp = self.comparison()
        # A equality is of the following form: comparison (("!=" | "==") comparison) *
        while self.match([TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL]):
            operator = self.previous()
            right = self.comparison()
            exp = expr.Binary(left=exp, operator=operator, right=right)
        return exp

    def comparison(self) -> expr.Expr:
        exp = self.term()
        while self.match(
            [
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
            ]
        ):
            operator = self.previous()
            right = self.term()
            exp = expr.Binary(left=exp, operator=operator, right=right)
        return exp

    def term(self) -> expr.Expr:
        exp = self.factor()
        while self.match([TokenType.MINUS, TokenType.PLUS]):
            operator = self.previous()
            right = self.factor()
            exp = expr.Binary(left=exp, operator=operator, right=right)
        return exp

    def factor(self) -> expr.Expr:
        exp = self.unary()
        while self.match([TokenType.STAR, TokenType.SLASH]):
            operator = self.previous()
            right = self.unary()
            exp = expr.Binary(left=exp, operator=operator, right=right)
        return exp

    def unary(self) -> expr.Expr:
        if self.match([TokenType.BANG, TokenType.NOT, TokenType.MINUS]):
            operator = self.previous()
            right = self.unary()
            return expr.Unary(operator=operator, right=right)

        return self.primary()

    def primary(self) -> expr.Expr:
        if self.match([TokenType.FALSE]):
            return expr.Literal(value=False)

        if self.match([TokenType.TRUE]):
            return expr.Literal(value=True)

        if self.match([TokenType.NIL]):
            return expr.Literal(value=None)

        if self.match([TokenType.NUMBER, TokenType.STRING]):
            return expr.Literal(value=self.previous().literal)

        if self.match([TokenType.LEFT_PAREN]):
            exp = self.expression()
            # If right parenthesis is not found, it's an error
            if not self.match([TokenType.RIGHT_PAREN]):
                raise ParserException(
                    "Could not find closing ')' after expression", token=self.previous()
                )
            return expr.Grouping(exp)

        raise ParserException("Invalid syntax", token=self.previous())
