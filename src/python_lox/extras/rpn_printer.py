from typing import override
from ..ast import expr as Expr


class RPNPrinter(Expr.Visitor[str]):
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

