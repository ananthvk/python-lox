import sys
from typing import Dict, Final, List, TextIO, TypeGuard, override

from .ast import expr as Expr
from .ast import stmt as Stmt
from .callable import ArrowFunction, Callable, LoxFunction
from .environment import Environment
from .error_reporter import ErrorReporter
from .exceptions import (
    BreakException,
    ContinueException,
    ReturnException,
    RuntimeException,
)
from .lox_class import LoxClass, LoxInstance
from .native_functions import native_functions
from .token import Token, TokenType

"""
NOTES:
1) Operations are only permitted between instances of the same class
    This means that you cannot add a number to a string, or compare a string with a number

2) No automatic conversion of integer to string
"""


class Interpreter(Expr.Visitor[object], Stmt.Visitor[None]):
    def __init__(
        self, error_reporter: ErrorReporter | None = None, stdout: TextIO = sys.stdout
    ) -> None:
        super().__init__()
        self.error_reporter = error_reporter
        self.stdout = stdout
        self.globals: Final = Environment()
        self.environment = self.globals
        self.nesting: Dict[int, int] = {}

        for function in native_functions:
            self.globals.declare(function.name())
            self.globals.define(function.name(), function)

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
                raise RuntimeException(
                    'Syntax Error: Invalid unary operator "-" for type',
                    token=expr.operator,
                )
            case TokenType.BANG:
                return not self.is_truthy(right)
            case TokenType.NOT:
                return not self.is_truthy(right)
            case TokenType.TYPEOF:
                if isinstance(right, bool):
                    return "bool"
                if isinstance(right, int) or isinstance(right, float):
                    return "number"
                if isinstance(right, str):
                    return "str"
                if isinstance(right, LoxFunction) or isinstance(right, ArrowFunction):
                    return "function"
                if right is None:
                    return "nil"
                else:
                    raise RuntimeError("Cannot find type of given object")
            case _:
                raise AssertionError("Logic error: Invalid unary operator")
        return None

    @override
    def visit_binary_expr(self, expr: Expr.Binary) -> object:
        if expr.operator.token_type == TokenType.COMMA:
            self.evaluate(expr.left)
            return self.evaluate(expr.right)

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
                f"Runtime Error: Operator {expr.operator.string_repr} not supported between different types",
                token=expr.operator,
            )

        match expr.operator.token_type:
            case TokenType.MINUS:
                if self.is_numeric(left):
                    return left - right  # type: ignore
                raise RuntimeException(
                    'Type Error: Operator "-" not valid between the operands',
                    token=expr.operator,
                )
            case TokenType.STAR:
                if self.is_numeric(left):
                    return left * right  # type: ignore
                raise RuntimeException(
                    'Type Error: Operator "*" not valid between the operands',
                    token=expr.operator,
                )
            case TokenType.SLASH:
                if self.is_numeric(left):
                    try:
                        return left / right  # type: ignore
                    except ZeroDivisionError:
                        raise RuntimeException(
                            "Runtime Error: Divide by Zero Error: division by zero",
                            token=expr.operator,
                        )

                raise RuntimeException(
                    'Type Error: Operator "/" not valid between the operands',
                    token=expr.operator,
                )
            case TokenType.PERCENTAGE:
                return left % right  # type: ignore
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
                    f'Syntax Error: Invalid operator "{expr.operator.string_repr}"',
                    token=expr.operator,
                )

    @override
    def visit_assign_expr(self, expr: Expr.Assign) -> object:
        nesting = self.nesting[id(expr)]
        value = self.evaluate(expr.value)
        self.environment.assign_at(nesting, expr.name, value)
        return value

    @override
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
        if obj1 is None:
            return False
        if obj2 is None:
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
        return type(obj1) is type(obj2)

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

    @override
    def visit_expression_stmt(self, stmt: Stmt.Expression) -> None:
        self.evaluate(stmt.expression)

    @override
    def visit_print_stmt(self, stmt: Stmt.Print) -> None:
        result = self.evaluate(stmt.expression)
        print(self.stringify(result), file=self.stdout, end="")

    @override
    def visit_println_stmt(self, stmt: Stmt.Println) -> None:
        result = self.evaluate(stmt.expression)
        print(self.stringify(result), file=self.stdout)

    @override
    def visit_var_stmt(self, stmt: Stmt.Var) -> None:
        self.environment.declare(stmt.name)
        if stmt.initializer:
            result = self.evaluate(stmt.initializer)
            self.environment.define(stmt.name, result)

    @override
    def visit_variable_expr(self, expr: Expr.Variable) -> object:
        return self.lookup_variable(expr.name, expr)

    @override
    def visit_block_stmt(self, stmt: Stmt.Block) -> None:
        env = Environment(parent=self.environment)
        self.execute_multiple_statements(stmt.statements, env)

    def execute_multiple_statements(
        self, stmts: List[Stmt.Stmt], env: Environment
    ) -> None:
        previous_env = self.environment
        try:
            self.environment = env
            for statement in stmts:
                self.execute(statement=statement)
        finally:
            self.environment = previous_env

    @override
    def visit_const_stmt(self, stmt: Stmt.Const) -> None:
        self.environment.declare(stmt.name)
        self.environment.define(stmt.name, self.evaluate(stmt.initializer))

    @override
    def visit_if_stmt(self, stmt: Stmt.If) -> None:
        result = self.evaluate(stmt.condition)
        if self.is_truthy(result):
            self.execute(stmt.if_branch)
        elif stmt.else_branch:
            self.execute(stmt.else_branch)

    @override
    def visit_while_stmt(self, stmt: Stmt.While) -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            try:
                self.execute(stmt.body)
            except BreakException:
                break
            except ContinueException:
                continue

    @override
    def visit_for_stmt(self, stmt: Stmt.For) -> None:
        if stmt.initializer:
            self.execute(stmt.initializer)
        while self.is_truthy(self.evaluate(stmt.condition) if stmt.condition else True):
            try:
                self.execute(stmt.body)
                if stmt.update:
                    self.evaluate(stmt.update)
            except BreakException:
                break
            except ContinueException:
                if stmt.update:
                    self.evaluate(stmt.update)
                continue

    @override
    def visit_break_stmt(self, stmt: Stmt.Break) -> None:
        raise BreakException()

    @override
    def visit_continue_stmt(self, stmt: Stmt.Continue) -> None:
        raise ContinueException()

    @override
    def visit_logical_expr(self, expr: Expr.Logical) -> object:
        left = self.evaluate(expr.left)

        if expr.operator.token_type == TokenType.OR:
            # For or operator, if left is true, return it, and do not evaluate the rest
            if self.is_truthy(left):
                return left
        else:
            # For and operator, if left is false, return it and do not evaluate the rest
            if not self.is_truthy(left):
                return left
        return self.evaluate(expr.right)

    @override
    def visit_assert_stmt(self, stmt: Stmt.Assert) -> None:
        if not self.is_truthy(self.evaluate(stmt.expression)):
            if stmt.message_expression:
                raise RuntimeException(
                    f"Assertion Error: {self.evaluate(stmt.message_expression)}",
                    exp=stmt.expression,
                )
            else:
                raise RuntimeException("Assertion Error: ", exp=stmt.expression)

    @override
    def visit_call_expr(self, expr: Expr.Call) -> object:
        callee = self.evaluate(expr.callee)
        args: List[object] = []
        for arg in expr.args:
            args.append(self.evaluate(arg))
        if not isinstance(callee, Callable):
            raise RuntimeException(
                f'Runtime Exception: Can only call functions and classes, but got "{type(callee).__name__}"',
                token=expr.paren,
            )
        if len(args) != callee.arity():
            message = ""
            if len(args) < callee.arity():
                message = "Too few arguments"
            else:
                message = "Too many arguments"
            raise RuntimeException(
                f"Runtime Exception: {message}. Expected {callee.arity()} arguments, got {len(args)} arguments",
                token=expr.paren,
            )
        return callee.call(self, args)

    @override
    def visit_function_stmt(self, stmt: Stmt.Function) -> None:
        function = LoxFunction(declaration=stmt, closure=self.environment)
        self.environment.declare(stmt.name)
        self.environment.define(stmt.name, function)

    @override
    def visit_arrow_expr(self, expr: Expr.Arrow) -> object:
        return ArrowFunction(declaration=expr, closure=self.environment)

    @override
    def visit_return_stmt(self, stmt: Stmt.Return) -> None:
        value = None
        if stmt.value:
            value = self.evaluate(stmt.value)
        raise ReturnException(value=value)

    @override
    def visit_class_stmt(self, stmt: Stmt.Class) -> None:
        self.environment.declare(stmt.name)

        methods: Dict[str, LoxFunction] = {}
        static_methods: Dict[str, LoxFunction] = {}
        getters: Dict[str, LoxFunction] = {}
        base_class: LoxClass | None = None

        if stmt.base_class is not None:
            cls = self.evaluate(stmt.base_class)
            if not isinstance(cls, LoxClass):
                raise RuntimeException(
                    f'Error: class "{stmt.name.string_repr}" cannot derive from "{stmt.base_class.name.string_repr}" since "{stmt.base_class.name.string_repr}" is not a class',
                    token=stmt.name,
                )
            base_class = cls

        for method in stmt.methods:
            function = LoxFunction(
                closure=self.environment,
                declaration=method,
                is_initializer=(method.name.string_repr == "init"),
            )
            methods[method.name.string_repr] = function

        for static_method in stmt.static_methods:
            function = LoxFunction(
                closure=self.environment,
                declaration=static_method,
                is_initializer=False,
            )
            static_methods[static_method.name.string_repr] = function

        for getter in stmt.getters:
            function = LoxFunction(
                closure=self.environment,
                declaration=getter,
                is_initializer=False,
            )
            getters[getter.name.string_repr] = function

        classobj = LoxClass(
            stmt.name.string_repr, methods, getters=getters, base_class=base_class
        )
        classobj.class_.methods = static_methods
        self.environment.define(stmt.name, classobj)

    @override
    def visit_get_expr(self, expr: Expr.Get) -> object:
        obj = self.evaluate(expr.obj)
        if not isinstance(obj, LoxInstance):
            raise RuntimeException(
                "Only instances of class have fields", token=expr.name
            )

        return obj.get(expr.name, self)

    @override
    def visit_set_expr(self, expr: Expr.Set) -> object:
        obj = self.evaluate(expr.obj)
        if not isinstance(obj, LoxInstance):
            raise RuntimeException(
                "Only instances of class have fields", token=expr.name
            )
        value = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    @override
    def visit_this_expr(self, expr: Expr.This) -> object:
        return self.lookup_variable(expr.keyword, expr)

    @override
    def visit_super_expr(self, expr: Expr.Super) -> object:
        return self.lookup_variable(expr.keyword, expr)

    def execute(self, statement: Stmt.Stmt) -> None:
        statement.accept(self)

    def interpret(self, statements: List[Stmt.Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)

        except RuntimeException as e:
            if self.error_reporter is None:
                raise e
            self.error_reporter.report("error", f"{e}", token=e.token)

    def resolve(self, expr: Expr.Expr, nesting: int) -> None:
        self.nesting[id(expr)] = nesting

    def lookup_variable(self, name: Token, expr: Expr.Expr) -> object:
        nesting = self.nesting[id(expr)]
        return self.environment.get_at(nesting, name)
