from typing import Callable, Dict
from utils.types import DnpData, VarData, Variable, DoubleBitTable
from pydnp3 import opendnp3


class DnpToVariableConv:
    """
    Class to create a Variable from a DnpData.
    The sole purpose of this class is improve code readability.
    """

    _initialized: bool = False
    _switch: Dict[type, Callable[[DnpData], VarData]] = {}

    def __init__(self):

        if self._initialized:
            return

        switch = {
            opendnp3.Binary: self._get_binary,
            opendnp3.DoubleBitBinary: self._get_double_bit,
            opendnp3.Counter: self._get_counter,
            opendnp3.FrozenCounter: self._get_frozen_counter,
            opendnp3.Analog: self._get_analog,
            opendnp3.BinaryOutputStatus: self._get_binary_output_status,
            opendnp3.AnalogOutputStatus: self._get_analog_output_status,
        }

        self._set_switch(switch)

    @classmethod
    def _set_switch(cls, switch: Dict[type, Callable[[DnpData], VarData]]):
        cls._switch = switch
        cls._initialized = True

    def get_value(self, dnp_var: DnpData, group: int, index: int) -> Variable:
        """
        Create a Variable from a DnpData value, a group and a index.

        Args:
            dnp_var (DnpData): Data value of the variable.
            group (int): Group of the variable.
            index (int): Index point of the variable.
            return (variable): The created Variable.

        """
        path = f"/{group}/{index}"

        # Don't catch the ValueError
        value = self._switch[type(dnp_var)](dnp_var)

        return Variable(path=path, value=value)

    @staticmethod
    def _get_binary(dnp_var: opendnp3.Binary) -> VarData:
        return dnp_var.value

    @staticmethod
    def _get_double_bit(dnp_var: opendnp3.DoubleBitBinary) -> VarData:
        return DoubleBitTable.index(dnp_var.value)

    @staticmethod
    def _get_counter(dnp_var: opendnp3.Counter) -> VarData:
        return dnp_var.value

    @staticmethod
    def _get_frozen_counter(dnp_var: opendnp3.FrozenCounter) -> VarData:
        return dnp_var.value

    @staticmethod
    def _get_analog(dnp_var: opendnp3.Analog) -> VarData:
        return dnp_var.value

    @staticmethod
    def _get_binary_output_status(dnp_var: opendnp3.BinaryOutputStatus) -> VarData:
        return dnp_var.value

    @staticmethod
    def _get_analog_output_status(dnp_var: opendnp3.AnalogOutputStatus) -> VarData:
        return dnp_var.value


class VariableToDnpConv:
    """
    Class to create a DnpData from a group (int) and a var (Variable).
    The sole purpose of this class is to prevent recalculate the switch and
    improve code readability.
    """

    _initialized: bool = False
    _switch: Dict[int, Callable[[Variable], VarData]] = {}

    def __init__(self):
        if self._initialized:
            return

        # Table of groups and function to handle the type
        # TODO: Outputs here? (12, 13, 41, 42, 43)
        group_ranges: Dict[int, Callable[[Variable], VarData]] = {
            range(1, 3): self._get_binary_value,  # Binary Input
            range(3, 5): self._get_double_bit_value,  # Double-bit Binary
            range(10, 14): self._get_binary_output_value,  # Binary Output
            range(20, 21): self._get_counter_value,  # Counter
            range(21, 22): self._get_frozen_counter_value,  # Frozen Counter
            range(22, 23): self._get_counter_value,  # Counter
            range(23, 24): self._get_frozen_counter_value,  # Frozen Counter
            range(30, 35): self._get_analog_value,  # Analog Input
            range(40, 41): self._get_analog_output_status_value,  # Analog Output Status
        }

        switch = {num: value for rng, value in group_ranges.items() for num in rng}
        self._set_switch(switch)

    @classmethod
    def _set_switch(cls, switch: Dict[int, Callable[[Variable], VarData]]):
        cls._switch = switch
        cls._initialized = True

    def get_value(self, group: int, var: Variable) -> DnpData:
        """
        Create a DnpData from a group number and a var (Variable).

        Args:
            group (int): Group of the variable. To define the point type.
            var (Variable): The variable with the data in a common type.
            return (DnpData): The DNP3 variable.
        """

        try:
            return self._switch[group](var)

        # Don't catch ValueError
        except KeyError as bad_index:
            raise ValueError from bad_index

    @staticmethod
    def _get_binary_value(var: Variable) -> opendnp3.Binary:
        # Binary Input
        if not isinstance(var.value, bool):
            raise ValueError

        return opendnp3.Binary(var.value)

    @staticmethod
    def _get_double_bit_value(var: Variable) -> opendnp3.DoubleBitBinary:
        # Double-bit binary
        # Double bit is transformed to int
        if not isinstance(var.value, int):
            raise ValueError

        try:
            return opendnp3.DoubleBitBinary(DoubleBitTable[var.value])
        except IndexError as bad_index:
            raise ValueError from bad_index

    @staticmethod
    def _get_binary_output_value(var: Variable) -> opendnp3.BinaryOutputStatus:
        # Binary Output
        if not isinstance(var.value, bool):
            raise ValueError

        return opendnp3.BinaryOutputStatus(var.value)

    @staticmethod
    def _get_counter_value(var: Variable) -> opendnp3.Counter:
        # Counter
        if not isinstance(var.value, int) or var.value < 0:
            raise ValueError

        return opendnp3.Counter(var.value)

    @staticmethod
    def _get_frozen_counter_value(var: Variable) -> opendnp3.FrozenCounter:
        # Counter
        if not isinstance(var.value, int) or var.value < 0:
            raise ValueError

        return opendnp3.Counter(var.value)

    @staticmethod
    def _get_analog_value(var: Variable) -> opendnp3.Analog:
        # Analog Input
        if not isinstance(var.value, (float, int)):
            raise ValueError

        return opendnp3.Analog(float(var.value))

    @staticmethod
    def _get_analog_output_status_value(var: Variable) -> opendnp3.AnalogOutputStatus:
        # Analog Output Status
        if not isinstance(var.value, (float, int)):
            raise ValueError

        print("HOLA: ", var.value)
        return opendnp3.AnalogOutputStatus(float(var.value))


class DnpVariable:
    """
    Implementation of the DNP3 variable to convert from a
    variable to a DNP3 variable.
    """

    def __init__(self, var: Variable) -> None:
        self.index: int
        self.group: int
        self.period: int
        self.value: DnpData

        self._group_valuator = VariableToDnpConv()

        self._set_info(var)
        self._set_value(var)

    def __str__(self) -> str:
        """
        Get the string representation of a DnpVariable.
        """
        return f"({self.group} | {self.index} | {self.value})"

    def _set_value(self, var: Variable) -> None:
        """
        Create and set a DnpData from the variable.
        """
        self.value: DnpData

        # Don't catch errors
        self.value = self._group_valuator.get_value(self.group, var)

    def _set_info(self, var: Variable) -> None:
        """
        Extract the variable index from the 'path' and
        save it to the object.

        path: /{group}/{index}
        """
        self.perod = var.period

        spl = var.path.split("/")

        # The caller must manage the ValueError Exception
        self.index = int(spl[-1])
        self.group = int(spl[-2])
