from pydnp3 import opendnp3
from utils.logger import Logger
from utils.types import Variable, IndexedDnpData
from node.variable import DnpToVariableConv, DnpVariable
from typing import Callable, Tuple


class SOEHandler(opendnp3.ISOEHandler):
    """
    Override ISOEHandler in this manner to implement application-specific sequence-of-events behavior.
    This is an interface for SequenceOfEvents (SOE) callbacks from the Master stack to the application layer.
    In other words, this class handle the new messages from the Oustation.
    """

    def __init__(self) -> None:
        # ISOEHandler __init__
        super().__init__()
        # Init the logger
        self._logger = Logger("SOEH")
        self._converter = DnpToVariableConv()

    def _var_handler(self, gv: Tuple[int, int], ivar: IndexedDnpData) -> None:
        """
        Handle new variable update.
        Convert the variable and send it to the manager.
        """
        if isinstance(ivar.value, opendnp3.TimeAndInterval):
            self._logger.log(f"Update: {gv[0]} | {gv[1]} | {ivar.index} | {ivar.value.time.value}")
        elif isinstance(ivar.value, opendnp3.OctetString):
            self._logger.error("Error creating variable from update: Unsoported OctetStrin")
            return
        else:
            self._logger.log(f"Update: {gv[0]} | {gv[1]} | {ivar.index} | {ivar.value.value}")

    @staticmethod
    def _parse_gv(gv: opendnp3.GroupVariation) -> Tuple[int, int]:
        """Convert from opendnp3.GroupVariation to a tuple of (group:int, variarion:int)"""
        group = int(int(gv) / 2 ** 8)
        variation = int(gv) & 0xFF
        return (group, variation)

    def Process(self, info: opendnp3.HeaderInfo, values) -> None:
        """
        Callback to process measurement data.
        Overrided from ISOEHandler.

        Args:
            info: (opendnp3.HeaderInfo): Information abaut the packet
            values (some ICollectionIndexed...): the indexed list of values.
        """

        gv: Tuple[int, int] = self._parse_gv(info.gv)
        handle = lambda v: self._var_handler(gv, v)

        values.ForeachItem(handle)

    def Start(self) -> None:
        """
        Start of a secuence of packets.
        Overrided from ISOEHandler.
        """
        self._logger.debug("In SOEHandler.Start")

    def End(self) -> None:
        """
        End of a secuence of packets.
        Overrided from ISOEHandler.
        """
        self._logger.debug("In SOEHandler.End")
