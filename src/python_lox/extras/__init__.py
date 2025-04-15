from ..lexer import Lexer
from ..parser import Parser
from . import ast_printer
from . import rpn_printer


def astprint(code: str) -> str:
    """
    Parses the given code into AST, and returns it in prefix notation
    """
    lexer = Lexer(code)
    parser = Parser(lexer.process())
    printer = ast_printer.ASTPrinter()
    return printer.print(parser.expression())


def rpnprint(code: str) -> str:
    """
    Parses the given code into AST, and returns it in postfix notation
    """
    lexer = Lexer(code)
    parser = Parser(lexer.process())
    printer = rpn_printer.RPNPrinter()
    return printer.convert(parser.expression())
