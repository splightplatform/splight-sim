from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union, Callable
from pydnp3 import opendnp3
from pydnp3.opendnp3 import DoubleBit

OUTSTATION_TYPE = "SERVER"
MASTER_TYPE = "CLIENT"


DnpData = Union[
    opendnp3.Binary,
    opendnp3.DoubleBitBinary,
    opendnp3.Analog,
    opendnp3.Counter,
    opendnp3.FrozenCounter,
    opendnp3.BinaryOutputStatus,
    opendnp3.AnalogOutputStatus,
    opendnp3.TimeAndInterval,
]

IndexedDnpData = Union[
    opendnp3.IndexedBinary,
    opendnp3.IndexedDoubleBitBinary,
    opendnp3.IndexedAnalog,
    opendnp3.IndexedCounter,
    opendnp3.IndexedFrozenCounter,
    opendnp3.IndexedBinaryOutputStatus,
    opendnp3.IndexedAnalogOutputStatus,
    opendnp3.IndexedTimeAndInterval,
]

DnpCommand = Union[
    opendnp3.ControlRelayOutputBlock,
    opendnp3.AnalogOutputDouble64,
    opendnp3.AnalogOutputFloat32,
    opendnp3.AnalogOutputInt16,
    opendnp3.AnalogOutputInt32,
]

VarData = Union[int, float, str, bool]

DoubleBitTable = [DoubleBit.INTERMEDIATE, DoubleBit.DETERMINED_OFF, DoubleBit.DETERMINED_ON, DoubleBit.INDETERMINATE]


@dataclass
class Variable:
    """
    Abstraction of the splight-protocol message.

    Attributes:
        path (str): Unique path to the variable.
        value (VarData): Value of the variable.
    """

    path: str
    value: VarData = -1
    period: int = -1


class Node(ABC):
    """
    Server/Client abstraction of the splight-protocol node.
    """
    def shutdown(self) -> None:
        """Clean and shutdown the node."""
