from typing import override, List
from ..ast import expr as Expr


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
        if expr.value is None:
            return "nil"
        if isinstance(expr.value, bool):
            return str(expr.value).lower()
        if isinstance(expr.value, float) or isinstance(expr.value, int):
            return f"{expr.value}"
        return str(expr.value)

    @override
    def visit_ternary_expr(self, expr: Expr.Ternary) -> str:
        return self.parenthesize("?:", expr.condition, expr.if_branch, expr.else_branch)

    @override
    def visit_variable_expr(self, expr: Expr.Variable) -> str:
        return f"var {expr.name.string_repr}"

    @override
    def visit_unary_expr(self, expr: Expr.Unary) -> str:
        return self.parenthesize(expr.operator.string_repr, expr.right)

    def parenthesize(self, name: str, *args: Expr.Expr) -> str:
        result: List[str] = []
        for expression in args:
            result.append(expression.accept(self))

        return f"({name} {' '.join(result)})"

    @override
    def visit_assign_expr(self, expr: Expr.Assign) -> str:
        return self.parenthesize(f"= {expr.name.string_repr}", expr.value)

    @override
    def visit_logical_expr(self, expr: Expr.Logical) -> str:
        return self.parenthesize(expr.operator.string_repr, expr.left, expr.right)

    @override
    def visit_call_expr(self, expr: Expr.Call) -> str:
        return self.parenthesize("function", expr.callee, *expr.args)
