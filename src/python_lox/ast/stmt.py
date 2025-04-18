from typing import Generic, TypeVar, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
from ..token import Token
from .expr import Expr

T = TypeVar('T')


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
    def visit_block_stmt(self, stmt: "Block") -> T:
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
class Block(Stmt):
    statements: List[Stmt]

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_block_stmt(self)

