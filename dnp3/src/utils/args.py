from dataclasses import dataclass
from typing import Any
import os


@dataclass
class Argument:
    """Class to handle arguments from the enviroment."""

    name: str
    value_type: type = Any
    prefix: str = "NODE"
    _value: Any = None

    @property
    def value(self) -> Any:
        """Get the value from the enviroment."""
        value = os.getenv(f"{self.prefix}_{self.name.upper()}", None)

        if value is not None:
            try:
                value = self.value_type(value)
            except TypeError as error:
                raise TypeError(f"Bad argument type: {self.name}") from error

        return value


class ArgumentParser:
    """Argument parser from the enviroment."""

    def __init__(self, prefix: str = "NODE"):
        self._arguments: list[Argument] = []
        self._prefix = prefix

    def add_argument(self, **kwargs):
        """Add new argument."""
        kwargs["prefix"] = self._prefix
        self._arguments.append(Argument(**kwargs))

    def parse_args(self) -> dict:
        """Create a dict of arguments from the enviroment."""
        args_dict: dict = {}

        for arg in self._arguments:
            value = arg.value
            if value is not None:
                args_dict[arg.name] = value

        return args_dict
