from io import StringIO
from python_lox.interpreter import Interpreter
from python_lox.lexer import Lexer
from python_lox.parser import Parser


def interpret(source: str):
    lexer = Lexer(source)
    parser = Parser(lexer.process())
    expr = parser.parse()
    if expr is None:
        raise RuntimeError()

    outfile = StringIO()

    interpreter = Interpreter(stdout=outfile)
    interpreter.interpret(expr)
    outfile.seek(0)
    return outfile.read()
