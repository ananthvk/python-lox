from typing import Generic, TypeVar, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
from ..token import Token
from .expr import Expr


T = TypeVar("T")


class Visitor(ABC, Generic[T]):
    @abstractmethod
    def visit_expression_stmt(self, stmt: "Expression") -> T:
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt: "Print") -> T:
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt: "Var") -> T:
        pass

    @abstractmethod
    def visit_const_stmt(self, stmt: "Const") -> T:
        pass

    @abstractmethod
    def visit_block_stmt(self, stmt: "Block") -> T:
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt: "If") -> T:
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt: "While") -> T:
        pass

    @abstractmethod
    def visit_for_stmt(self, stmt: "For") -> T:
        pass

    @abstractmethod
    def visit_break_stmt(self, stmt: "Break") -> T:
        pass

    @abstractmethod
    def visit_continue_stmt(self, stmt: "Continue") -> T:
        pass

    @abstractmethod
    def visit_assert_stmt(self, stmt: "Assert") -> T:
        pass


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor[T]) -> T:
        pass


@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_expression_stmt(self)


@dataclass
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_print_stmt(self)


@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr | None = None

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_var_stmt(self)


@dataclass
class Const(Stmt):
    name: Token
    initializer: Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_const_stmt(self)


@dataclass
class Block(Stmt):
    statements: List[Stmt]

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_block_stmt(self)


@dataclass
class If(Stmt):
    condition: Expr
    if_branch: Block
    else_branch: Block | None = None

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_if_stmt(self)


@dataclass
class While(Stmt):
    condition: Expr
    body: Block

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_while_stmt(self)


@dataclass
class For(Stmt):
    body: Block
    initializer: Stmt | None = None
    condition: Expr | None = None
    update: Expr | None = None

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_for_stmt(self)


@dataclass
class Break(Stmt):

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_break_stmt(self)


@dataclass
class Continue(Stmt):

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_continue_stmt(self)


@dataclass
class Assert(Stmt):
    expression: Expr
    message_expression: Expr | None = None

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_assert_stmt(self)
