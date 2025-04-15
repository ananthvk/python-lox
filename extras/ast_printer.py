from typing import override, List
from python_lox.ast import expr as Expr
from python_lox.token import TokenType, Token
from python_lox.parser import Parser
from python_lox.lexer import Lexer


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
        return str(expr.value)

    @override
    def visit_unary_expr(self, expr: Expr.Unary) -> str:
        return self.parenthesize(expr.operator.string_repr, expr.right)

    def parenthesize(self, name: str, *args: Expr.Expr) -> str:
        result: List[str] = []
        for expression in args:
            result.append(expression.accept(self))

        return f"({name} {' '.join(result)})"


while True:
    inp = input(">>> ")
    if not inp:
        continue
    if inp == "exit":
        break
    lexer = Lexer(inp)
    parser = Parser(lexer.process())
    printer = ASTPrinter()
    print(printer.print(parser.expression()))
