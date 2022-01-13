from pydnp3 import opendnp3
from utils.logger import Logger
from utils.types import DnpCommand, VarData, Variable
from node.variable import DnpVariable
from typing import Callable, Union
from random import random


class CommandHandler(opendnp3.ICommandHandler):
    """
    Handle Select and Operate commands and send it to the manager.

    ICommandHandler implements the Outstation's handling of Select and Operate,
    which relay commands and data from the Master to the Outstation.
    """

    def __init__(self):
        super().__init__()
        self._logger = Logger("CMDHDLR")
        self._selected: tuple(Union[DnpCommand, None], int) = (None, 0)

    def set_update(self, update: Callable[[DnpVariable], None]) -> None:
        """Set the variable apdate method."""
        self._update = update

    def _update(self, _: DnpVariable) -> None:
        """Apply variable update in the node."""
        return

    @staticmethod
    def _cmd_to_str(command: DnpCommand) -> str:
        """Return a string representation of a command."""

        if isinstance(command, opendnp3.ControlRelayOutputBlock):
            return f"CROB | {command.functionCode}"

        return f"ANALOG | {command.value}"

    def _operate(self, command: DnpCommand, index: int) -> None:
        if isinstance(command, opendnp3.ControlRelayOutputBlock):
            if index > 4:
                value = command.functionCode in [opendnp3.ControlCode.LATCH_ON, opendnp3.ControlCode.PULSE_ON]
                group = 1
            else:
                value = ramdom() * 100
                group = 30
        else:
            value = command.value
            group = 30

        var = Variable(path=f"/{group}/{index}", value=value)
        dnp_var = DnpVariable(var)

        self._update(dnp_var)

    def Start(self) -> None:
        """
        Called on command frame start.
        Overrided from ICommandHandler.
        """
        self._logger.debug("In OutstationCommandHandler.Start")

    def End(self) -> None:
        """
        Called on command frame end.
        Overrided from ICommandHandler.
        """
        self._logger.debug("In OutstationCommandHandler.End")

    def Select(self, command: DnpCommand, index: int) -> opendnp3.CommandStatus:
        """
        Handle an Select command from the master.
        Overrided from ICommandHandler.

        Args:
            command (DnpCommand): Command itself.
            index (int): Index of the target point.
            return (opendnp3.CommandStatus): Result of the Select operation.
        """
        self._logger.log(f"CMD: SELECT | {self._cmd_to_str(command)} | {index}")
        self._selected = (command, index)
        return opendnp3.CommandStatus.SUCCESS

    def _command_is_selected(self, cmd: DnpCommand, index: int) -> bool:
        """
        Check if the command is equal to the last selected.
        Used to check the Select Before Operate.
        """
        if index != self._selected[1]:
            return False

        return cmd == self._selected[0]

    def Operate(self, command: DnpCommand, index: int, op_type: opendnp3.OperateType) -> opendnp3.CommandStatus:
        """
        Handle an Operate command from the Master.
        Overrided from ICommandHandler.

        Args:
            command (DnpCommand): Command itself.
            index (int): Index of the target point.
            op_type (OperateType): Type of operation. Direct, Direct no ACK, Select Before Operate.
            return (opendnp3.CommandStatus): Result of the Select operation.
        """
        self._logger.log(f"CMD: OPERATE | {self._cmd_to_str(command)} | {index}")

        # Check if the command has been selected
        if op_type == opendnp3.OperateType.SELECT_BEFORE_OPERATE and not self._command_is_selected(command, index):
            self._logger.error("Trying to operate unselected command.")
            return opendnp3.CommandStatus.NO_SELECT

        self._operate(command, index)
        self._logger.success("Operate success")

        return opendnp3.CommandStatus.SUCCESS
