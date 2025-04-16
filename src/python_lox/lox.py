from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter
from .error_reporter import ErrorReporter


class Lox:
    version = "0.1.0"
    build_date = "12 April 2025 17:01:30"

    def __init__(self, error_reporter: ErrorReporter) -> None:
        self.error_reporter = error_reporter
        self.interpreter = Interpreter(error_reporter=error_reporter)

    def run(self, source: str) -> int:
        """
        Execute the source program
        """
        lexer = Lexer(source, self.error_reporter)
        tokens = lexer.process()
        parser = Parser(tokens, self.error_reporter)
        expr = parser.parse()
        if expr is not None:
            output = self.interpreter.interpret(expr)
            if not self.error_reporter.is_error:
                print(output)
                
        return 0
