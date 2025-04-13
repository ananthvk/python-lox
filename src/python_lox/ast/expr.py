from typing import Any, Generic, TypeVar
from dataclasses import dataclass
from abc import ABC, abstractmethod
from ..token import Token


class Expr(ABC):
    def __init__(self):
        if type(self) is Expr:
            raise TypeError("Expr is an abstract base class, cannot instantiate it")


T = TypeVar('T')


class Visitor(ABC, Generic[T]):
    @abstractmethod
    def visit_binary_expr(self, expr: 'Binary') -> T:
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: 'Grouping') -> T:
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: 'Literal') -> T:
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: 'Unary') -> T:
        pass


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_binary_expr(self)

@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_grouping_expr(self)

@dataclass
class Literal(Expr):
    value: Any

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_literal_expr(self)

@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_unary_expr(self)
