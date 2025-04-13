from typing import Any
from dataclasses import dataclass
from abc import ABC
from ..token import Token


class Expr(ABC):
    pass


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass
class Grouping(Expr):
    expression: Expr


@dataclass
class Literal(Expr):
    value: Any


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr
