from ..lexer import Lexer
from ..parser import Parser
from . import ast_printer


def astprint(code: str) -> str:
    """
    Parses the given code into AST, and returns it in prefix notation
    """
    lexer = Lexer(code)
    parser = Parser(lexer.process())
    printer = ast_printer.ASTPrinter()
    return printer.print(parser.expression())
