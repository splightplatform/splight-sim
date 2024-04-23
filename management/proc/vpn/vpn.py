from abc import ABC, abstractmethod

from proc import Proc
from utils import Logger


class Vpn(Proc, ABC):
    """
    VPN abstract class.

    Args:
        ns (str): Namespace or network name.
        file (str): Path to the vpn file (optional).
        user (str): Vpn username (optional).
        pass (str): Vpn password (optional).
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

        self._ns = kwargs["ns"]
        self._file = kwargs["file"]
        self._user = kwargs["user"]
        self._pass = kwargs["pass"]
        self._popen = None

        self._logger = Logger("Vpn " + self._ns)
        self._logger.log("Created")

    @abstractmethod
    def connect(self) -> None:
        """Connect to the VPN."""

    def __del__(self) -> None:
        self._logger.log("Killing vpn")
