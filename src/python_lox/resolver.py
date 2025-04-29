from typing import TYPE_CHECKING, Dict, Final, List, override

from .ast import expr as Expr
from .ast import stmt as Stmt
from .error_reporter import ErrorReporter
from .exceptions import NameException
from .token import Token

if TYPE_CHECKING:
    from .interpreter import Interpreter


class Resolver(Expr.Visitor[None], Stmt.Visitor[None]):
    def __init__(
        self, interpreter: "Interpreter", error_reporter: ErrorReporter | None = None
    ) -> None:
        self.interpreter: Final["Interpreter"] = interpreter
        self.scopes: List[Dict[str, bool]] = []
        self.error_reporter = error_reporter

    def resolve(self, obj: Stmt.Stmt | Expr.Expr | List[Stmt.Stmt]) -> None:
        try:
            if isinstance(obj, list):
                for item in obj:
                    self.resolve(item)
            else:
                obj.accept(self)
        except NameException as e:
            if self.error_reporter:
                self.error_reporter.report("error", str(e), e.token)
            else:
                raise e

    def begin_scope(self) -> None:
        self.scopes.append({})

    def end_scope(self) -> None:
        self.scopes.pop()

    def declare(self, name: Token) -> None:
        scope = self.scopes[-1]
        """
        False indicates that the variable is present in the innermost scope, and that it shadows a variable
        in the outer scope, but is not yet ready used.
        """
        scope[name.string_repr] = False

    def define(self, name: Token) -> None:
        """
        After running the initializer and setting the value, the variable is ready for use, so we mark it as true
        """
        scope = self.scopes[-1]
        scope[name.string_repr] = True

    def resolve_local(self, expr: Expr.Expr, name: Token) -> None:
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.string_repr in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

        """
        The name was not resolved: Note I have decided to make my interpreter stricter, i.e. it does not assume
        that the variable is available globally.
        """
        raise NameException(
            f'Name Error: Access of undefined variable. "{name.string_repr}" was not found in current scope"',
            token=name,
        )

    def resolve_function(self, params: List[Token], body: List[Stmt.Stmt]) -> None:
        self.begin_scope()
        for param in params:
            self.declare(param)
            self.define(param)
        self.resolve(body)
        self.end_scope()

    @override
    def visit_block_stmt(self, stmt: Stmt.Block) -> None:
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    @override
    def visit_var_stmt(self, stmt: Stmt.Var) -> None:
        self.declare(stmt.name)
        if stmt.initializer:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    @override
    def visit_const_stmt(self, stmt: Stmt.Const) -> None:
        # TODO: Actually implement this
        self.declare(stmt.name)
        if stmt.initializer:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    @override
    def visit_variable_expr(self, expr: Expr.Variable) -> None:
        """
        If the variable is declared, but not yet defined, it means that the variable is being used in it's own initializer
        """
        is_defined = self.scopes[-1].get(expr.name.string_repr)
        if is_defined is not None and is_defined is False:
            raise NameException(
                f"Name Error: Variable {expr.name.string_repr} is being used in its own initializer",
                token=expr.name,
            )
        self.resolve_local(expr, expr.name)

    @override
    def visit_assign_expr(self, expr: Expr.Assign) -> None:
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)

    @override
    def visit_function_stmt(self, stmt: Stmt.Function) -> None:
        """
        Declare and define the function before it's scope so that recursion is possible
        """
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt.params, stmt.body)

    @override
    def visit_arrow_expr(self, expr: Expr.Arrow) -> None:
        self.resolve_function(expr.params, expr.body)

    @override
    def visit_assert_stmt(self, stmt: Stmt.Assert) -> None:
        self.resolve(stmt.expression)

    @override
    def visit_binary_expr(self, expr: Expr.Binary) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    @override
    def visit_break_stmt(self, stmt: Stmt.Break) -> None:
        pass

    @override
    def visit_call_expr(self, expr: Expr.Call) -> None:
        self.resolve(expr.callee)
        for arg in expr.args:
            self.resolve(arg)

    @override
    def visit_continue_stmt(self, stmt: Stmt.Continue) -> None:
        pass

    @override
    def visit_expression_stmt(self, stmt: Stmt.Expression) -> None:
        self.resolve(stmt.expression)

    @override
    def visit_for_stmt(self, stmt: Stmt.For) -> None:
        if stmt.initializer:
            self.resolve(stmt.initializer)
        if stmt.condition:
            self.resolve(stmt.condition)
        if stmt.update:
            self.resolve(stmt.update)
        self.resolve(stmt.body)

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
        self.resolve(stmt.body)
