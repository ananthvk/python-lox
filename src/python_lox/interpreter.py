from .ast import expr as Expr
from .token import TokenType
from .error_reporter import ErrorReporter
from typing import override, TypeGuard

"""
NOTES:
1) Operations are only permitted between instances of the same class
    This means that you cannot add a number to a string, or compare a string with a number

2) No automatic conversion of integer to string
"""


class RuntimeException(Exception):
    def __init__(self, message: str, exp: Expr.Expr) -> None:
        super().__init__(message)
        self.exp = exp


class Interpreter(Expr.Visitor[object]):

    def __init__(self, error_reporter: ErrorReporter | None = None) -> None:
        super().__init__()
        self.error_reporter = error_reporter

    @override
    def visit_literal_expr(self, expr: Expr.Literal) -> object:
        return expr.value

    @override
    def visit_grouping_expr(self, expr: Expr.Grouping) -> object:
        return self.evaluate(expr.expression)

    @override
    def visit_unary_expr(self, expr: Expr.Unary) -> object:
        right = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.MINUS:
                if self.is_numeric(right):
                    return -right
                raise RuntimeException('Invalid unary operator "-" for type', expr)
            case TokenType.BANG:
                return not self.is_truthy(right)
            case TokenType.NOT:
                return not self.is_truthy(right)
            case _:
                raise AssertionError("Logic error: Invalid unary operator")
        return None

    @override
    def visit_binary_expr(self, expr: Expr.Binary) -> object:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case _:
                pass

        if not self.is_same_type(left, right):
            raise RuntimeException(
                f"Operator {expr.operator.string_repr} not supported between different types",
                expr,
            )

        match expr.operator.token_type:
            case TokenType.MINUS:
                if self.is_numeric(left):
                    return left - right  # type: ignore
                raise RuntimeException(
                    'Type Error: Operator "-" not valid between the operands', expr
                )
            case TokenType.STAR:
                if self.is_numeric(left):
                    return left * right  # type: ignore
                raise RuntimeException(
                    'Type Error: Operator "*" not valid between the operands', expr
                )
            case TokenType.SLASH:
                if self.is_numeric(left):
                    return left / right  # type: ignore
                raise RuntimeException(
                    'Type Error: Operator "/" not valid between the operands', expr
                )
            case TokenType.PLUS:
                return left + right  # type: ignore

            case TokenType.GREATER:
                return left > right  # type: ignore
            case TokenType.GREATER_EQUAL:
                return left >= right  # type: ignore
            case TokenType.LESS:
                return left < right  # type: ignore
            case TokenType.LESS_EQUAL:
                return left <= right  # type: ignore
            case _:
                raise RuntimeException(
                    f'Invalid operator "{expr.operator.string_repr}"', expr
                )

    def visit_ternary_expr(self, expr: Expr.Ternary) -> object:
        condition = self.evaluate(expr.condition)
        if self.is_truthy(condition):
            if_branch = self.evaluate(expr.if_branch)
            return if_branch

        else_branch = self.evaluate(expr.else_branch)
        return else_branch

    def is_truthy(self, obj: object) -> bool:
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def is_equal(self, obj1: object, obj2: object) -> bool:
        if obj1 is None and obj2 is None:
            return True
        if obj1 == None:
            return False
        if obj2 == None:
            return False

        # Similar to python, return False if the type of objects are different
        if not self.is_same_type(obj1, obj2):
            return False
        if self.is_numeric(obj1) and self.is_numeric(obj2):
            if obj1.is_integer() and obj2.is_integer():
                return int(obj1) == int(obj2)
        return obj1 == obj2

    def evaluate(self, expr: Expr.Expr) -> object:
        return expr.accept(self)

    def is_same_type(self, obj1: object, obj2: object) -> bool:
        # Treat int and float as numeric, just the internal representation is different
        if self.is_numeric(obj1) and self.is_numeric(obj2):
            return True
        return type(obj1) == type(obj2)

    def is_numeric(self, obj: object) -> TypeGuard[float | int]:
        return isinstance(obj, int) or isinstance(obj, float)

    def is_string(self, obj: object) -> TypeGuard[str]:
        return isinstance(obj, str)

    def stringify(self, obj: object) -> str:
        if obj is None:
            return "nil"
        if isinstance(obj, bool):
            if obj:
                return "true"
            return "false"
        if self.is_numeric(obj):
            return f"{obj}"
        return str(obj)

    def interpret(self, expr: Expr.Expr) -> str:
        try:
            value = self.evaluate(expr)
            return self.stringify(value)
        except RuntimeException as e:
            if self.error_reporter is None:
                raise e
            self.error_reporter.report("error", f"{e}")
        return ""
