import typer
import sys
from rich import print
from .lox import Lox
from typing_extensions import Annotated

app = typer.Typer()


@app.command("")
def main(file: Annotated[str, typer.Argument(help="Run this script")] = ""):
    """
    Run FILE in script mode if FILE is provided. Otherwise run in interactive mode
    """

    lox = Lox()

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


def run():
    app()


if __name__ == "__main__":
    run()
