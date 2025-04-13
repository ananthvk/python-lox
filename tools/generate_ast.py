import typer
from typing import List, Tuple
from pathlib import Path
from rich import print

ast_classes = {
    "expr": {
        "binary": [
            # Variable name, Type hints, Default value (if any)
            ("left", "Expr"),
            ("operator", "Token"),
            ("right", "Expr"),
        ],
        "grouping": [("expression", "Expr")],
        "literal": [("value", "Any")],
        "unary": [("operator", "Token"), ("right", "Expr")],
    }
}

module_header = """from typing import Any
from dataclasses import dataclass
from abc import ABC
from ..token import Token


"""


def class_template(module_name: str, class_name: str, attributes: List[Tuple[str, str]]):
    attribute_strings: List[str] = []
    for attribute in attributes:
        attribute_strings.append(f'    {attribute[0]}: {attribute[1]}')
            
    return f"""
@dataclass
class {class_name.capitalize()}({module_name}):
{'\n'.join(attribute_strings)}

"""


def main(output_directory: Path):
    print(f"[green]Creating directory [bold]{output_directory}[/bold]")
    output_directory.mkdir(parents=True, exist_ok=True)
    for module, v in ast_classes.items():
        with open(output_directory / f"{module}.py", "w") as outfile:
            outfile.write(module_header)
            outfile.write(f'class {module.capitalize()}(ABC):\n    pass\n\n')
            for cls, attrs in v.items():
                outfile.write(class_template(module.capitalize(), cls, attrs))


if __name__ == "__main__":
    typer.run(main)
