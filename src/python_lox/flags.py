"""
For now hardcode this dictionary, in the future accept these flags as command line args or from a config file
"""

from typing import Any, Dict

values: Dict[str, Any] = {"Wunused": True, "Wshadow": True}


class Flags:
    def get_bool(self, key: str) -> bool:
        return values.get(key, False)  # type: ignore
