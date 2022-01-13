from typing import Callable
from node.outstation.commands import CommandHandler
from node.variable import DnpVariable
from node.outstation.application import OutstationApplication
from node.channel import ChannelListener
from utils.logger import Logger
from utils.types import Node, Variable
from node.logger import ApplicationLogger
from pydnp3 import opendnp3, openpal, asiopal, asiodnp3


class Outstation(Node):
    """
    DNP3 outstation class.
    Implementation of a DNP3 virtual outstation (server).

    Args:
        host (str = "0.0.0.0"): ip address of the oustation.
        port (int = 20000): ip address of the oustation.
        local_addr (int = 10): DNP3 address of the outstation.
        remote_addr (int = 1): DNP3 address of the master.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 20000, local_addr: int = 10, remote_addr: int = 1) -> None:
        # Init the logger
        self._logger = Logger("OUTSTATION")
        # Amount of variables of each type
        self._var_len = 10

        # Init DNP3 stack config
        self._logger.log("Configuring the DNP3 stack.")
        self._stack_config: asiodnp3.OutstationStackConfig = self._configure_stack(local_addr, remote_addr)

        # Set variables grops and variations
        self._logger.log("Configuring the outstation database.")
        self._configure_database(self._stack_config.dbConfig)

        self._logger.log("Creating a DNP3Manager.")
        # First arg is threads_to_allocat
        self._outstation_logger = ApplicationLogger()
        self._manager = asiodnp3.DNP3Manager(1, self._outstation_logger)

        # Create the channel (TCP)
        self._logger.log(f"Creating the DNP3 channel, a TCP server on {host}:{port}")
        self._retry_parameters = asiopal.ChannelRetry().Default()
        self._listener = ChannelListener()
        self._channel: asiodnp3.IChannel = self._manager.AddTCPServer(
            "server",
            opendnp3.levels.NORMAL | opendnp3.levels.ALL_COMMS,
            self._retry_parameters,
            host,
            port,
            self._listener,
        )

        # Create CommandHandler
        self._logger.log("Adding the outstation to the channel.")
        self._command_handler = CommandHandler()
        self._application = OutstationApplication()
        self._outstation = self._channel.AddOutstation(
            "outstation", self._command_handler, self._application, self._stack_config
        )

        self._command_handler.set_update(self._apply_update)

        # Finally enable the oustation
        self._logger.log("Enabling the outstation. Traffic will now start to flow.")
        self._outstation.Enable()

    def _configure_stack(self, local_addr: int, remote_addr: int) -> asiodnp3.OutstationStackConfig:
        """
        Set up the OpenDNP3 configuration.

        Args:
            local_addr (int): DNP3 address of the outstation.
            remote_addr (int): DNP3 address of the master.

        Default:
            * 10 variables of each point type.
            * Event buffer of 10 elements for each point type.
            * Allow unsolicited messages.
        """
        stack_config = asiodnp3.OutstationStackConfig(opendnp3.DatabaseSizes.AllTypes(self._var_len))
        stack_config.outstation.eventBufferConfig = opendnp3.EventBufferConfig().AllTypes(self._var_len)
        stack_config.outstation.params.allowUnsolicited = True
        stack_config.link.LocalAddr = local_addr
        stack_config.link.RemoteAddr = remote_addr
        stack_config.link.KeepAliveTimeout = openpal.TimeDuration().Max()
        return stack_config

    def _configure_database(self, db_config: asiodnp3.DatabaseConfig) -> None:
        """
        Configure the Outstation's database of input point definitions.
        This will configure the variations for static and event points.
        Now with the defaults.

        Args:
            db_config (asiodnp3.DatabaseConfig):
                Instance of the configuration where apply changes.

        Defaults:
            analog          ->  static: Group30Var6,  event: Group32Var6 (In the splight-pydnp3)
            aostatus        ->  static: Group40Var4,  event: Group42Var6 (In the splight-pydnp3)
            binary          ->  static: Group1Var2,   event: Group2Var1
            bostatus        ->  static: Group10Var2,  event: Group11Var1
            counter         ->  static: Group20Var1,  event: Group22Var1
            doubleBinary    ->  static: Group3Var2,   event: Group4Var1
            frozenCounter   ->  static: Group21Var1,  event: Group23Var1
            sizes           ->  static: Group110Var0, event: Group111Var0
            timeAndInterval ->  static: Group50Var4
        """
        # Examples:
        #  Configure two Analog points (group/variation 30.1) at indexe 1.
        #  db_config.analog[1].clazz = opendnp3.PointClass.Class2
        #  db_config.analog[1].svariation = opendnp3.StaticAnalogVariation.Group30Var1
        #  db_config.analog[1].evariation = opendnp3.EventAnalogVariation.Group32Var7
        #  Configure two Binary points (group/variation 1.2) at indexe 1.
        #  db_config.binary[1].clazz = opendnp3.PointClass.Class2
        #  db_config.binary[1].svariation = opendnp3.StaticBinaryVariation.Group1Var2
        #  db_config.binary[1].evariation = opendnp3.EventBinaryVariation.Group2Var2

    def shutdown(self) -> None:
        """Shutdown the Outstation."""
        self._logger.log("Exiting application...")
        self._logger.log("Shutting down stack config...")
        del self._stack_config
        self._logger.log("Shutting down channel...")
        del self._channel
        self._logger.log("Shutting down outstation...")
        del self._outstation
        self._logger.log("Shutting down DNP3Manager...")
        self._manager.Shutdown()
        del self._manager
        self._logger.success("Bye")

    def _apply_update(self, var: DnpVariable) -> None:
        """
        Apply some change to a variable.

        Args:
            var (DnpVariable): Target variable with his value.
        """
        self._logger.log(f"Recording {var} measurement")

        builder = asiodnp3.UpdateBuilder()
        builder.Update(var.value, var.index)
        update = builder.Build()
        self._outstation.Apply(update)
