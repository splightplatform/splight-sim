from typing import Callable
from node.channel import ChannelListener
from node.logger import ApplicationLogger
from node.master.application import MasterApplication
from node.master.soe import SOEHandler
from node.variable import DnpVariable, VarData
from pydnp3 import asiodnp3, asiopal, opendnp3, openpal
from utils.logger import Logger
from utils.types import DnpCommand, Node, Variable


def command_callback(self, result: opendnp3.ICommandTaskResult = None) -> None:
    """
    Function to handle callbacks from the commands sended to the master.
    Due to a error on the pybind11 binding, this needs to be outside
    the Master class.

    More info on: pydnp3/src/opendnp3/master/ICommandProcessor.h:265
    TODO: Fix it
    """
    if result is not None:
        print(f"Command result: {opendnp3.TaskCompletionToString(result.summary)}")


class Master(Node):
    """
    DNP3 Master class.
    Implementation of a DNP3 virtual master (client).

    Args:
        host (str = "127.0.0.1"): ip address of the oustation.
        port (int = 20000): ip address of the oustation.
        local_addr (int = 1): DNP3 address of the outstation.
        remote_addr (int = 10): DNP3 address of the master.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 20000, local_addr: int = 1, remote_addr: int = 10) -> None:
        # Init the logger
        self._logger = Logger("MASTER")

        # Init DNP3 stack config
        self._logger.log("Configuring the DNP3 stack.")
        self._stack_config: asiodnp3.MasterStackConfig = self._configure_stack(local_addr, remote_addr)

        self._logger.log("Creating a DNP3Manager.")
        # First arg is threads_to_allocat
        self._application_logger = ApplicationLogger()
        self._manager = asiodnp3.DNP3Manager(1, self._application_logger)

        # Create the channel (TCP)
        self._logger.log("Creating the DNP3 channel, a TCP client.")
        self._retry_parameters = asiopal.ChannelRetry().Default()
        self._listener = ChannelListener()
        self._channel: asiodnp3.IChannel = self._manager.AddTCPClient(
            "client",
            opendnp3.levels.NORMAL | opendnp3.levels.ALL_COMMS,
            self._retry_parameters,
            host,
            "0.0.0.0",  # All the interfaces
            port,
            self._listener,
        )

        # Create SOE Handler
        self._logger.log("Creating the SOEHandler.")
        self._soe_handler = SOEHandler()
        self._logger.log("Creating the MasterApplication.")
        self._application = MasterApplication()

        # Add the master to the channel
        self._master = self._channel.AddMaster("master", self._soe_handler, self._application, self._stack_config)

        # Finally enable the oustation
        self._logger.log("Enabling the master. Traffic will now start to flow.")
        self._master.Enable()

    @staticmethod
    def _configure_stack(local_addr: int, remote_addr: int) -> asiodnp3.MasterStackConfig:
        """
        Set up the OpenDNP3 configuration.

        Args:
            remote_addr (int): DNP3 address of the master.

        Default:
            * Not disable unsolicited messages on start
        """
        stack_config = asiodnp3.MasterStackConfig()
        stack_config.master.responseTimeout = openpal.TimeDuration().Seconds(2)
        stack_config.master.disableUnsolOnStartup = False
        stack_config.link.RemoteAddr = remote_addr
        return stack_config

    def shutdown(self):
        """Shutdown the Outstation."""
        self._logger.log("Exiting application...")
        self._logger.log("Shutting down stack config...")
        del self._stack_config
        self._logger.log("Shutting down channel...")
        del self._channel
        self._logger.log("Shutting down master...")
        del self._master
        self._logger.log("Shutting down DNP3Manager...")
        self._manager.Shutdown()
        self._logger.success("Bye")

    def scan(self, group: int, variation: int, index: int, count: int = 1) -> None:
        """
        Create new scan. This will make a request to the outstation.

        Args:
            group (int): Group of the point.
            variation (int): Variation of the point.
            index (int): Index of the point
            count (int): The amount of points to scan.
        """
        self._logger.debug(f"Creating scan to group {group}, variation {variation}, index {index}")
        self._master.ScanRange(
            opendnp3.GroupVariationID(group, variation),
            index, index + count - 1,
            opendnp3.TaskConfig().Default()
        )

    def operate(self, group: int, index: int, value: VarData) -> None:
        """Apply the 'write' action to a Variable."""

        command: DnpCommand

        # Create the command
        if group == 41:
            # Analog Output
            try:
                command = opendnp3.AnalogOutputDouble64(float(value))

            except ValueError:
                self._logger.error("Bad variable type on operate.")
                return

        elif group == 12:
            # Binary Output
            try:
                command = opendnp3.ControlRelayOutputBlock(
                    opendnp3.ControlCode.PULSE_ON if value in ["true", "True"] else opendnp3.ControlCode.PULSE_OFF
                )

            except ValueError:
                self._logger.error("Bad variable type on operate.")
                return

        else:
            self._logger.error(f"Bad group ({group}) on operate.")
            return

        # Direct operate
        config = opendnp3.TaskConfig().Default()
        self._master.DirectOperate(command, index, command_callback, config)
        self._logger.success("Command operated on group {dnp_var.group}, index {dnp_var.index}")
