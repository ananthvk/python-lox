from .lexer import Lexer
from .parser import Parser
from .extras.ast_printer import ASTPrinter


class Lox:
    version = "0.1.0"
    build_date = "12 April 2025 17:01:30"

    def run(self, source: str) -> int:
        """
        Execute the source program
        """
        lexer = Lexer(source)
        tokens = lexer.process()
        parser = Parser(tokens)
        expr = parser.parse()
        printer = ASTPrinter()
        print(printer.print(expr))
        return 0
