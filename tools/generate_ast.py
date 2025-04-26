import typer
from typing import List, Tuple, Dict, Any
from pathlib import Path
from rich import print

ast_classes: Dict[str, Any] = {
    "expr": {
        "binary": [
            # Variable name, Type hints, Default value (if any)
            ("left", "Expr"),
            ("operator", "Token"),
            ("right", "Expr"),
        ],
        "assign": [("name", "Token"), ("value", "Expr")],
        "ternary": [
            ("condition", "Expr"),
            ("if_branch", "Expr"),
            ("else_branch", "Expr"),
        ],
        "grouping": [("expression", "Expr")],
        "literal": [("value", "object")],
        "unary": [("operator", "Token"), ("right", "Expr")],
        "variable": [("name", "Token")],
        "logical": [
            # Variable name, Type hints, Default value (if any)
            ("left", "Expr"),
            ("operator", "Token"),
            ("right", "Expr"),
        ],
        "call": [("callee", "Expr"), ("paren", "Token"), ("args", "List[Expr]")],
    },
    "stmt": {
        "expression": [("expression", "Expr")],
        "print": [("expression", "Expr")],
        "println": [("expression", "Expr")],
        "var": [("name", "Token"), ("initializer", "Expr | None = None")],
        "const": [("name", "Token"), ("initializer", "Expr")],
        "block": [("statements", "List[Stmt]")],
        "if": [
            ("condition", "Expr"),
            ("if_branch", "Block"),
            ("else_branch", "Block | None = None"),
        ],
        "while": [("condition", "Expr"), ("body", "Block")],
        "for": [
            ("body", "Block"),
            ("initializer", "Stmt | None = None"),
            ("condition", "Expr | None = None"),
            ("update", "Expr | None = None"),
        ],
        "break": [],
        "continue": [],
        "assert": [
            ("expression", "Expr"),
            ("message_expression", "Expr | None = None"),
        ],
        "function": [
            ("name", "Token"),
            ("params", "List[Token]"),
            ("body", "List[Stmt]"),
        ],
        "return": [("keyword", "Token"), ("value", "Expr | None = None")],
    },
}

module_header = """from typing import Generic, TypeVar, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
from ..token import Token

"""


def base_class_template(module: str):
    return f"""
class {module.capitalize()}(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor[T]) -> T:
        pass

"""


def class_template(module: str, class_name: str, attributes: List[Tuple[str, str]]):
    attribute_strings: List[str] = []
    for attribute in attributes:
        attribute_strings.append(f"    {attribute[0]}: {attribute[1]}")

    return f"""
@dataclass
class {class_name.capitalize()}({module.capitalize()}):
{'\n'.join(attribute_strings)}

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_{class_name}_{module}(self)

"""


def visitor_template(module: str, classes: List[str]):
    methods: List[str] = []
    for cls in classes:
        methods += [
            f'    @abstractmethod\n    def visit_{cls}_{module}(self, {module}: "{cls.capitalize()}") -> T:\n        pass\n'
        ]

    return f"""
T = TypeVar('T')


class Visitor(ABC, Generic[T]):
{'\n'.join(methods)}
"""


def main(output_directory: Path):
    print(f"[green]Creating directory [bold]{output_directory}[/bold]")
    output_directory.mkdir(parents=True, exist_ok=True)
    for module, v in ast_classes.items():
        with open(output_directory / f"{module}.py", "w") as outfile:
            outfile.write(module_header)
            outfile.write(visitor_template(module, list(v.keys())))
            outfile.write(base_class_template(module))
            for cls, attrs in v.items():
                outfile.write(class_template(module, cls, attrs))


if __name__ == "__main__":
    typer.run(main)
