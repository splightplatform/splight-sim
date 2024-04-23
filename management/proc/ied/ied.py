from abc import ABC, abstractmethod

from proc import Proc
from utils import Logger


class Ied(Proc, ABC):
    """
    Abstract IED class.

    Args:
        port (int): Port where bind the Ied.
        namespace (str): Namespace/network where bind the Ied.
    """

    def __init__(self, port: int, namespace: str) -> None:
        super().__init__()

        self._port = port
        self._ns = namespace
        self._popen = None

        self._logger = Logger(f"Ied {port}")

    @abstractmethod
    def start(self) -> None:
        """Start the Ied instance."""

    def __del__(self) -> None:
        self._logger.log("Killing ied")
        if self._popen is not None:
            self._popen.kill()
