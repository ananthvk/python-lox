from typing import override
from python_lox.ast import expr as Expr
from python_lox.lexer import Lexer


class RPNConverter(Expr.Visitor[str]):
    """
    Given an AST, convert it to reverse polish notation
    Reverse polish notation is post order of the abstract syntax tree
    """

    def convert(self, expr: Expr.Expr) -> str:
        return expr.accept(self)

    @override
    def visit_binary_expr(self, expr: Expr.Binary) -> str:
        return f"{expr.left.accept(self)} {expr.right.accept(self)} {expr.operator.string_repr}"

    @override
    def visit_grouping_expr(self, expr: Expr.Grouping) -> str:
        return expr.expression.accept(self)

    @override
    def visit_literal_expr(self, expr: Expr.Literal) -> str:
        return str(expr.value)

    @override
    def visit_unary_expr(self, expr: Expr.Unary) -> str:
        return f"{expr.operator.string_repr} {expr.right.accept(self)}"


#              01 2 34 5 67 8 910
lexer = Lexer("(1 + 2) * (4 - 3)")
tokens = lexer.process()
expression = Expr.Binary(
    left=Expr.Grouping(
        Expr.Binary(
            left=Expr.Literal(tokens[1].literal),
            operator=tokens[2],
            right=Expr.Literal(tokens[3].literal),
        )
    ),
    operator=tokens[5],
    right=Expr.Grouping(
        Expr.Binary(
            left=Expr.Literal(tokens[7].literal),
            operator=tokens[8],
            right=Expr.Literal(tokens[9].literal),
        )
    ),
)

converter = RPNConverter()
print(converter.convert(expression))
