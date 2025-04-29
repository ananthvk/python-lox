from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Dict, Final, List, override

from .ast import expr as Expr
from .ast import stmt as Stmt
from .error_reporter import ErrorLevel, ErrorReporter
from .exceptions import NameException
from .token import Token

if TYPE_CHECKING:
    from .interpreter import Interpreter


@dataclass
class IdentifierState:
    is_mutable: bool = False
    is_init: bool = False
    is_defined: bool = False


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()


class Resolver(Expr.Visitor[None], Stmt.Visitor[None]):
    def __init__(
        self, interpreter: "Interpreter", error_reporter: ErrorReporter | None = None
    ) -> None:
        self.interpreter: Final["Interpreter"] = interpreter
        self.scopes: List[Dict[str, IdentifierState]] = []
        self.error_reporter = error_reporter
        self.loop_depth = 0
        self.current_function = FunctionType.NONE

    def resolve(self, obj: Stmt.Stmt | Expr.Expr | List[Stmt.Stmt]) -> None:
        if isinstance(obj, list):
            for item in obj:
                self.resolve(item)
        else:
            obj.accept(self)

    def begin_scope(self) -> None:
        self.scopes.append({})

    def end_scope(self) -> None:
        self.scopes.pop()

    def declare(self, name: Token) -> None:
        scope = self.scopes[-1]
        scope[name.string_repr] = IdentifierState()

    def define(self, name: Token) -> None:
        scope = self.scopes[-1]
        if name.string_repr in scope:
            scope[name.string_repr].is_defined = True
        else:
            self.report_error(
                f"Error: Trying to define identifier {name.string_repr} without declaring it",
                token=name,
            )

    def resolve_local(
        self,
        expr: Expr.Expr,
        name: Token,
        should_be_init: bool = False,
        should_be_mutable: bool = False,
    ) -> None:
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.string_repr in self.scopes[i]:
                ident = self.scopes[i][name.string_repr]
                if should_be_init and not ident.is_init:
                    self.report_error(
                        f'Variable "{name.string_repr}" is not initialized', token=name
                    )
                if should_be_mutable and not ident.is_mutable:
                    self.report_error(
                        f'Variable "{name.string_repr}" is declared const, and cannot be modified',
                        token=name,
                    )
                ident.is_init = True
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

        """
        The name was not resolved: Note I have decided to make my interpreter stricter, i.e. it does not assume
        that the variable is available globally.
        """
        self.report_error(
            f'Name Error: Access of undefined variable. "{name.string_repr}" was not found in current scope',
            name,
        )

    def report_error(
        self, message: str, token: Token, severity: ErrorLevel = "error"
    ) -> None:
        if self.error_reporter:
            self.error_reporter.report(severity, message=message, token=token)
        else:
            raise NameException(
                message,
                token=token,
            )

    def resolve_function(
        self, params: List[Token], body: List[Stmt.Stmt], function_type: FunctionType
    ) -> None:
        enclosing = self.current_function
        self.current_function = function_type
        self.begin_scope()
        for param in params:
            self.declare(param)
            self.define(param)
            """
            Inside the function, all the parameter variables are initialized
            """
            self.scopes[-1][param.string_repr].is_init = True

        self.resolve(body)
        self.end_scope()
        self.current_function = enclosing

    @override
    def visit_block_stmt(self, stmt: Stmt.Block) -> None:
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    @override
    def visit_var_stmt(self, stmt: Stmt.Var) -> None:
        if stmt.name.string_repr in self.scopes[-1]:
            self.report_error(
                f'var "{stmt.name.string_repr}" has already been declared in this scope',
                token=stmt.name,
            )
        self.declare(stmt.name)

        if stmt.initializer:
            self.resolve(stmt.initializer)
            self.scopes[-1][stmt.name.string_repr].is_init = True

        self.define(stmt.name)
        self.scopes[-1][stmt.name.string_repr].is_mutable = True

    @override
    def visit_const_stmt(self, stmt: Stmt.Const) -> None:
        if stmt.name.string_repr in self.scopes[-1]:
            self.report_error(
                f'const "{stmt.name.string_repr}" has already been declared in this scope',
                token=stmt.name,
            )
        self.declare(stmt.name)
        if stmt.initializer:
            self.resolve(stmt.initializer)
            self.scopes[-1][stmt.name.string_repr].is_init = True
        self.define(stmt.name)

    @override
    def visit_variable_expr(self, expr: Expr.Variable) -> None:
        """
        If the variable is declared, but not yet defined, it means that the variable is being used in it's own initializer
        """

        ident = self.scopes[-1].get(expr.name.string_repr)
        if ident is not None and ident.is_defined is False:
            self.report_error(
                f"Name Error: Variable {expr.name.string_repr} is being used in its own initializer",
                token=expr.name,
            )
            return

        self.resolve_local(expr, expr.name, should_be_init=True)

    @override
    def visit_assign_expr(self, expr: Expr.Assign) -> None:
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name, should_be_mutable=True)

    @override
    def visit_function_stmt(self, stmt: Stmt.Function) -> None:
        """
        Declare and define the function before it's scope so that recursion is possible
        """
        # TODO: Fix bug where in the REPL, a function declaration fails, but does not allow redeclaration
        is_declared = self.scopes[-1].get(stmt.name.string_repr)
        if is_declared is not None:
            self.report_error(
                f"Name Error: function {stmt.name.string_repr} has already been declared in this scope",
                token=stmt.name,
            )

        self.declare(stmt.name)
        self.define(stmt.name)
        self.scopes[-1][stmt.name.string_repr].is_init = True
        self.resolve_function(stmt.params, stmt.body, FunctionType.FUNCTION)

    @override
    def visit_arrow_expr(self, expr: Expr.Arrow) -> None:
        self.resolve_function(expr.params, expr.body, FunctionType.FUNCTION)

    @override
    def visit_assert_stmt(self, stmt: Stmt.Assert) -> None:
        self.resolve(stmt.expression)

    @override
    def visit_binary_expr(self, expr: Expr.Binary) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    @override
    def visit_break_stmt(self, stmt: Stmt.Break) -> None:
        if self.loop_depth == 0:
            self.report_error(
                'Syntax Error: "break" statement outside a loop', token=stmt.keyword
            )

    @override
    def visit_call_expr(self, expr: Expr.Call) -> None:
        self.resolve(expr.callee)
        for arg in expr.args:
            self.resolve(arg)

    @override
    def visit_continue_stmt(self, stmt: Stmt.Continue) -> None:
        if self.loop_depth == 0:
            self.report_error(
                'Syntax Error: "continue" statement outside a loop', token=stmt.keyword
            )

    @override
    def visit_expression_stmt(self, stmt: Stmt.Expression) -> None:
        self.resolve(stmt.expression)

    @override
    def visit_for_stmt(self, stmt: Stmt.For) -> None:
        self.begin_scope()
        if stmt.initializer:
            self.resolve(stmt.initializer)
        if stmt.condition:
            self.resolve(stmt.condition)
        if stmt.update:
            self.resolve(stmt.update)

        self.loop_depth += 1
        self.resolve(stmt.body)
        self.loop_depth -= 1
        self.end_scope()

    @override
    def visit_grouping_expr(self, expr: Expr.Grouping) -> None:
        self.resolve(expr.expression)

    @override
    def visit_if_stmt(self, stmt: Stmt.If) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.if_branch)
        if stmt.else_branch:
            self.resolve(stmt.else_branch)

    @override
    def visit_literal_expr(self, expr: Expr.Literal) -> None:
        pass

    @override
    def visit_logical_expr(self, expr: Expr.Logical) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    @override
    def visit_print_stmt(self, stmt: Stmt.Print) -> None:
        self.resolve(stmt.expression)

    @override
    def visit_println_stmt(self, stmt: Stmt.Println) -> None:
        self.resolve(stmt.expression)

    @override
    def visit_return_stmt(self, stmt: Stmt.Return) -> None:
        if self.current_function == FunctionType.NONE:
            self.report_error(
                'Syntax Error: "return" statement outside a function',
                token=stmt.keyword,
            )
        if stmt.value:
            self.resolve(stmt.value)

    @override
    def visit_ternary_expr(self, expr: Expr.Ternary) -> None:
        self.resolve(expr.condition)
        self.resolve(expr.if_branch)
        self.resolve(expr.else_branch)

    @override
    def visit_unary_expr(self, expr: Expr.Unary) -> None:
        self.resolve(expr.right)

    @override
    def visit_while_stmt(self, stmt: Stmt.While) -> None:
        self.resolve(stmt.condition)
        self.loop_depth += 1
        self.resolve(stmt.body)
        self.loop_depth -= 1
