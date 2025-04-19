import typer
from pathlib import Path
from typing import List
from rich import print

"""
This script generates token definitions and token type enum
"""

TOKEN_FILE_NAME = "token.py"

tokendefs = {
    "keywords": {
        "and": "AND",
        "or": "OR",
        "not": "NOT",
        "false": "FALSE",
        "nil": "NIL",
        "true": "TRUE",
        "if": "IF",
        "else": "ELSE",
        "class": "CLASS",
        "fun": "FUN",
        "for": "FOR",
        "while": "WHILE",
        "print": "PRINT",
        "return": "RETURN",
        "super": "SUPER",
        "this": "THIS",
        "var": "VAR",
        "const": "CONST",
        "typeof": "TYPEOF",
    },
    "single_char_tokens": {
        "(": "LEFT_PAREN",
        ")": "RIGHT_PAREN",
        "{": "LEFT_BRACE",
        "}": "RIGHT_BRACE",
        ",": "COMMA",
        ".": "DOT",
        "-": "MINUS",
        "+": "PLUS",
        ";": "SEMICOLON",
        "*": "STAR",
        "!": "BANG",
        ">": "GREATER",
        "<": "LESS",
        "=": "EQUAL",
        ":": "COLON",
        "?": "QUESTION_MARK",
        "%": "PERCENTAGE",
    },
    "double_char_tokens": {
        "!=": "BANG_EQUAL",
        ">=": "GREATER_EQUAL",
        "<=": "LESS_EQUAL",
        "==": "EQUAL_EQUAL",
    },
    "misc": {
        "identifier": "IDENTIFIER",
        "number": "NUMBER",
        "eof": "EOF",
        "unknown": "UNKNOWN",
        "string": "STRING",
        "slash": "SLASH",
    },
}


def generate_token_types_class(token_types: List[str]) -> str:
    tokens = ["    " + i + " = auto()" for i in token_types]
    return f"""
from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
{'\n'.join(tokens)}
"""


token_class = """
@dataclass
class Token:
    token_type: TokenType = TokenType.UNKNOWN
    line: int = 0
    literal: int | float | str | None = None
    string_repr: str = ""
    start: int = 0
    end: int = 0

    def __repr__(self) -> str:
        if self.token_type == TokenType.IDENTIFIER:
            return f"<{self.token_type} {self.literal}>"
        elif self.token_type == TokenType.STRING:
            return f'<{self.token_type} "{self.literal}">'
        elif self.token_type == TokenType.NUMBER:
            if (
                isinstance(self.literal, float) or isinstance(self.literal, int)
            ):
                return f"<{self.token_type} {self.literal}>"

        return f"<{self.token_type}>"
"""


def main(output_directory: Path):
    print(f"[green]Creating directory [bold]{output_directory}[/bold]")
    output_directory.mkdir(parents=True, exist_ok=True)
    token_types: List[str] = []
    definitions: List[str] = []

    # Get all token types
    for section, v in tokendefs.items():
        definitions += [f"\n{section} = {{\n"]
        for token, val in v.items():
            token_types += [val]
            definitions += [f'    "{token}": TokenType.{val},\n']
        definitions += ["}\n"]

    token_types.sort()

    with open(output_directory / TOKEN_FILE_NAME, "w") as outfile:
        outfile.write(generate_token_types_class(token_types))
        outfile.write("".join(definitions))
        outfile.write(token_class)


if __name__ == "__main__":
    typer.run(main)
