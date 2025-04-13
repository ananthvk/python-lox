from .lexer import Lexer
from .ast import expr as Expr
from .token import TokenType, Token
from .ast_printer import ASTPrinter


class Lox:
    version = "0.1.0"
    build_date = "12 April 2025 17:01:30"

    def __init__(self) -> None:

        expression = Expr.Binary(
            Expr.Unary(
                Token(TokenType.MINUS, string_repr="-"), Expr.Literal(123)
            ),
            Token(TokenType.STAR, string_repr="*"),
            Expr.Grouping(Expr.Literal(45.67)),
        )

        printer = ASTPrinter()
        print(printer.print(expression))

    def run(self, source: str) -> int:
        """
        Execute the source program
        """
        lexer = Lexer(source)
        print(lexer.process())
        return 0
