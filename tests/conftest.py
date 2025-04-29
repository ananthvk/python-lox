import subprocess
from io import StringIO
from typing import List

from python_lox.interpreter import Interpreter
from python_lox.lexer import Lexer
from python_lox.parser import Parser
from python_lox.resolver import Resolver


def interpret(source: str):
    lexer = Lexer(source)
    parser = Parser(lexer.process())
    expr = parser.parse()
    if expr is None:
        raise RuntimeError()

    outfile = StringIO()

    interpreter = Interpreter(stdout=outfile)
    resolver = Resolver(interpreter)

    resolver.scopes.append({})
    for global_value in interpreter.globals.values.keys():
        resolver.scopes[0][global_value] = True
    resolver.resolve(expr)

    interpreter.interpret(expr)
    outfile.seek(0)
    return outfile.read()


def exec_command(args: List[str]):
    result = subprocess.run(args, capture_output=True)
    assert (
        result.returncode == 0
    ), f"{args[0]} failed with exit code {result.returncode}"  # fmt: skip
