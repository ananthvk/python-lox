from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Dict, Final, List, override

from .ast import expr as Expr
from .ast import stmt as Stmt
from .error_reporter import ErrorLevel, ErrorReporter
from .exceptions import NameException
from .flags import Flags
from .token import Token

if TYPE_CHECKING:
    from .interpreter import Interpreter


class IdentifierType(Enum):
    VARIABLE = auto()
    FUNCTION = auto()


@dataclass
class IdentifierState:
    is_mutable: bool = False
    is_init: bool = False
    is_defined: bool = False
    is_used: bool = False
    identifier_type: IdentifierType = IdentifierType.VARIABLE
    token: Token | None = None


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    INITIALIZER = auto()
    METHOD = auto()


class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class Resolver(Expr.Visitor[None], Stmt.Visitor[None]):
    def __init__(
        self, interpreter: "Interpreter", error_reporter: ErrorReporter | None = None
    ) -> None:
        self.interpreter: Final["Interpreter"] = interpreter
        self.scopes: List[Dict[str, IdentifierState]] = []
        self.error_reporter = error_reporter
        self.loop_depth = 0
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

        # TODO: Later pass the flags to the resolver class through the constructor (dependency injection)
        self.flags = Flags()

    def resolve(self, obj: Stmt.Stmt | Expr.Expr | List[Stmt.Stmt]) -> None:
        if isinstance(obj, list):
            for item in obj:
                self.resolve(item)
        else:
            obj.accept(self)

    def begin_scope(self) -> None:
        self.scopes.append({})

    def end_scope(self) -> None:
        if self.flags.get_bool("Wunused") and self.error_reporter:
            for i, identifier in self.scopes[-1].items():
                if not identifier.is_used:
                    self.error_reporter.report(
                        "warn",
                        f'-Wunused: Unused {identifier.identifier_type.name.lower()} "{i}"',
                        token=identifier.token,
                    )

        self.scopes.pop()

    def declare(self, name: Token) -> None:
        # Check for shadowing
        if self.flags.get_bool("Wshadow") and self.error_reporter:
            for i in range(len(self.scopes) - 1, -1, -1):
                value = self.scopes[i].get(name.string_repr)
                if value is not None:
                    self.error_reporter.report(
                        "warn",
                        f'-Wshadow: Declaration of local variable "{name.string_repr}" shadows previous declaration',
                        token=name,
                    )
                    self.error_reporter.report(
                        "warn",
                        f'-Wshadow: "{name.string_repr}" previously declared here',
                        token=value.token,
                    )

        scope = self.scopes[-1]
        scope[name.string_repr] = IdentifierState(token=name)

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
    ) -> bool:
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
                ident.is_used = True
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return True

        """
        The name was not resolved: Note I have decided to make my interpreter stricter, i.e. it does not assume
        that the variable is available globally.
        """
        self.report_error(
            f'Name Error: Access of undefined variable. "{name.string_repr}" was not found in current scope',
            name,
        )
        return False

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

        # TODO: Fix bug where if the initializer fails, the name is still reserved and cannot be declared again in REPL

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
        self.scopes[-1][stmt.name.string_repr].identifier_type = IdentifierType.FUNCTION
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
            if self.current_function == FunctionType.INITIALIZER:
                self.report_error(
                    "Syntax Error: Cannot return a value inside a constructor",
                    token=stmt.keyword,
                )
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

    @override
    def visit_class_stmt(self, stmt: Stmt.Class) -> None:
        # TODO: Fix bug where in the REPL, a function declaration fails, but does not allow redeclaration
        is_declared = self.scopes[-1].get(stmt.name.string_repr)
        if is_declared is not None:
            self.report_error(
                f"Name Error: class {stmt.name.string_repr} has already been declared in this scope",
                token=stmt.name,
            )

        enclosing = self.current_class
        self.current_class = ClassType.CLASS
        self.declare(stmt.name)
        self.define(stmt.name)
        self.scopes[-1][stmt.name.string_repr].is_init = True
        self.scopes[-1][stmt.name.string_repr].is_mutable = False

        if (
            stmt.base_class is not None
            and stmt.base_class.name.string_repr == stmt.name.string_repr
        ):
            self.report_error(
                f"Syntax Error: class {stmt.name.string_repr} inherits from itself",
                token=stmt.name,
            )

        if stmt.base_class is not None:
            self.current_class = ClassType.SUBCLASS
            self.resolve(stmt.base_class)

        # Before adding this, resolve all static methods
        # TODO: Note: what will happen if the class is defined inside another class? Static methods in the inner class should
        # not be able to access this of the outer class, but the current implementation does not prevent that. Fix it.
        for static_method in stmt.static_methods:
            if static_method.name.string_repr == "init":
                self.report_error(
                    "Syntax Error: init method cannot be static",
                    static_method.name,
                    "error",
                )
            self.resolve_function(
                params=static_method.params,
                body=static_method.body,
                function_type=FunctionType.METHOD,
            )

        self.begin_scope()
        self.scopes[-1]["this"] = IdentifierState(
            is_defined=True, is_init=True, is_mutable=False, is_used=True
        )

        if stmt.base_class is not None:
            self.scopes[-1]["super"] = IdentifierState(
                is_defined=True, is_init=True, is_mutable=False, is_used=True
            )

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.string_repr == "init":
                declaration = FunctionType.INITIALIZER
            self.resolve_function(
                params=method.params, body=method.body, function_type=declaration
            )

        for getter in stmt.getters:
            if getter.name.string_repr == "init":
                self.report_error(
                    "Syntax Error: init method cannot be a getter",
                    getter.name,
                    "error",
                )
            self.resolve_function(
                params=getter.params,
                body=getter.body,
                function_type=FunctionType.FUNCTION,
            )

        self.end_scope()
        self.current_class = enclosing

    @override
    def visit_get_expr(self, expr: Expr.Get) -> None:
        """
        Do not resolve the right side, since it is done dynamically, and not statically
        """
        self.resolve(expr.obj)

    @override
    def visit_set_expr(self, expr: Expr.Set) -> None:
        self.resolve(expr.value)
        self.resolve(expr.obj)

    @override
    def visit_this_expr(self, expr: Expr.This) -> None:
        if self.current_class == ClassType.NONE:
            self.report_error(
                'Syntax Error: "this" expression outside a class', token=expr.keyword
            )
            return
        self.resolve_local(expr, expr.keyword)

    @override
    def visit_super_expr(self, expr: Expr.Super) -> None:
        if self.current_class == ClassType.NONE:
            self.report_error(
                'Syntax Error: "super" expression outside a class', token=expr.keyword
            )
            return
        elif self.current_class == ClassType.CLASS:
            self.report_error(
                'Syntax Error: "super" expression inside class that does not have a base class',
                token=expr.keyword,
            )
            return
        elif self.current_class == ClassType.SUBCLASS:
            self.resolve_local(expr, expr.keyword)
