import typer
import os
import readline
import sys
from rich import print

from .lox import Lox
from .error_reporter import ErrorReporter
from typing_extensions import Annotated
import sys

app = typer.Typer()

HISTORY_FILE = os.path.expanduser("~/.loxhistory")

import atexit

atexit.register(lambda: readline.write_history_file(HISTORY_FILE))


def report_error(error_reporter: ErrorReporter, source: str) -> None:
    if error_reporter.is_error:
        for message in error_reporter.messages:
            token = message[2]
            extra_info: str = ""
            if token is None:
                extra_info = ""
            else:
                token_line, start, _ = error_reporter.get_token_line(source, token)
                if token_line:
                    squiggles = f'    {" " * len(str(token.line))}  {" " * (token.start - start)} {"^" * len(token.string_repr)}'
                    extra_info = f'at "{token.string_repr}"\n    {token.line} | {token_line}\n{squiggles}'

            if message[0] == "error":
                print(f"[red]{message[1]} {extra_info}[/red]")
            elif message[0] == "fatal":
                print(f"[bold][red]{message[1]} {extra_info}[/red][/bold]")
            else:
                print(f"[yellow]{message[1]} {extra_info}[/yellow]")

        if error_reporter.too_many_errors():
            print("[yellow] Too many errors. Further errors supressed [/yellow]")


@app.command("")
def main(file: Annotated[str, typer.Argument(help="Run this script")] = "") -> int:
    """
    Run FILE in script mode if FILE is provided. Otherwise run in interactive mode
    """

    error_reporter = ErrorReporter()

    lox = Lox(error_reporter)

    # Run in script mode
    if file:
        source = ""
        with open(file, "r") as f:
            source = f.read()
        exit_code = lox.run(source)
        report_error(error_reporter, source)
        if error_reporter.is_error:
            sys.exit(1)
        sys.exit(exit_code)

    # Load history
    if os.path.exists(HISTORY_FILE):
        readline.read_history_file(HISTORY_FILE)

    # Run in REPL mode
    print(
        f"[bold]Pylox[/bold] {lox.version} ({lox.build_date}) [Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}] on {sys.platform}"
    )
    print(f'Type [bold]"exit"[/bold] to exit the interpeter')

    while True:
        print(f"[blue]>>> ", end="")
        line = input()
        if line == "exit":
            break
        if line == "":
            continue
        lox.run(line)
        report_error(error_reporter, line)
        error_reporter.is_error = False
        error_reporter.messages.clear()
    return 0


def run() -> None:
    app()


if __name__ == "__main__":
    run()
