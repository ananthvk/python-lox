from .error_reporter import ErrorReporter
from .interpreter import Interpreter
from .lexer import Lexer
from .parser import Parser
from .resolver import IdentifierState, Resolver


class Lox:
    version = "0.1.0"
    build_date = "12 April 2025 17:01:30"

    def __init__(self, error_reporter: ErrorReporter) -> None:
        self.error_reporter = error_reporter
        self.interpreter = Interpreter(error_reporter=error_reporter)
        self.resolver = Resolver(self.interpreter, self.error_reporter)
        self.error_reporter.is_error = False
        self.error_reporter.messages.clear()
        self.resolver.scopes = []
        self.resolver.scopes.append({})
        for global_value in self.interpreter.globals.values.keys():
            self.resolver.scopes[0][global_value] = IdentifierState(
                is_init=True, is_defined=True, is_mutable=True
            )

    def run(self, source: str, repl: bool = False) -> int:
        """
        Execute the source program
        """
        lexer = Lexer(source, self.error_reporter)
        tokens = lexer.process()
        parser = Parser(tokens, self.error_reporter)
        statements = parser.parse(repl)
        if statements is None:
            return 1

        """
        Create a scope for the entire program
        """
        self.resolver.begin_scope()
        self.resolver.resolve(statements)
        self.resolver.end_scope()

        if self.error_reporter.is_error:
            return 1

        self.interpreter.interpret(statements)

        return 0
