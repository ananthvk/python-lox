from typing import override, List
from python_lox.ast import expr as Expr
from python_lox.token import TokenType, Token


class ASTPrinter(Expr.Visitor[str]):

    def print(self, expr: Expr.Expr) -> str:
        return expr.accept(self)

    @override
    def visit_binary_expr(self, expr: Expr.Binary) -> str:
        return self.parenthesize(expr.operator.string_repr, expr.left, expr.right)

    @override
    def visit_grouping_expr(self, expr: Expr.Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    @override
    def visit_literal_expr(self, expr: Expr.Literal) -> str:
        return str(expr.value)

    @override
    def visit_unary_expr(self, expr: Expr.Unary) -> str:
        return self.parenthesize(expr.operator.string_repr, expr.right)

    def parenthesize(self, name: str, *args: Expr.Expr) -> str:
        result: List[str] = []
        for expression in args:
            result.append(expression.accept(self))

        return f"({name} {' '.join(result)})"


expression = Expr.Binary(
    Expr.Unary(Token(TokenType.MINUS, string_repr="-"), Expr.Literal(123)),
    Token(TokenType.STAR, string_repr="*"),
    Expr.Grouping(Expr.Literal(45.67)),
)

printer = ASTPrinter()
print(printer.print(expression))
