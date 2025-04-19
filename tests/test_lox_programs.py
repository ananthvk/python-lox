from .conftest import exec_command
from typing import List
import os
import glob


def get_lox_files() -> List[str]:
    current_file_path = os.path.abspath(__file__)
    programs_dir = os.path.join(os.path.dirname(current_file_path), "programs")
    return glob.glob(os.path.join(programs_dir, "*.lox"))


def test_all():
    for file in get_lox_files():
        exec_command(["pylox", file])
