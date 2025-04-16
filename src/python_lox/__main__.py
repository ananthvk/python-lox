import typer
import sys
from rich import print

from .lox import Lox
from .error_reporter import ErrorReporter
from typing_extensions import Annotated

app = typer.Typer()


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
        return lox.run(source)

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
        if error_reporter.is_error:
            for message in error_reporter.messages:
                token = message[2]
                extra_info: str = ""
                if token is None:
                    extra_info = ""
                else:
                    token_line, start, _ = error_reporter.get_token_line(line, token)
                    if token_line:
                        squiggles = f'    {" " * len(str(token.line))}  {" " * (token.start - start)} {"^" * len(token.string_repr)}'
                        extra_info = f'at "{token.string_repr}"\n    {token.line} | {token_line}\n{squiggles}'

                if message[0] == "error":
                    print(f"[red]Syntax Error: {message[1]} {extra_info}[/red]")
                elif message[0] == "fatal":
                    print(
                        f"[bold][red]Syntax Error: {message[1]} {extra_info}[/red][/bold]"
                    )
                else:
                    print(f"[yellow]Syntax Error: {message[1]} {extra_info}[/yellow]")

            if error_reporter.too_many_errors():
                print("[yellow] Too many errors. Further errors supressed [/yellow]")
            error_reporter.is_error = False
            error_reporter.messages.clear()
    return 0


def run() -> None:
    app()


if __name__ == "__main__":
    run()
