from pydnp3 import opendnp3
from utils.logger import Logger


class OutstationApplication(opendnp3.IOutstationApplication):
    """IOutstationApplication custom instance for the Outstation"""

    def __init__(self):
        # Init the logger
        self._logger = Logger("OUTSTATION_APP")
        # IOutstationApplication __init__
        super().__init__()

    def GetApplicationIIN(self) -> opendnp3.ApplicationIIN:
        """
        Return the application-controlled IIN field.
        Overridden method.
        """
        application_iin = opendnp3.ApplicationIIN()
        application_iin.configCorrupt = False
        application_iin.deviceTrouble = False
        application_iin.localControl = False
        application_iin.needTime = False
        # Just for testing purposes, convert it to an IINField and display the contents of the two bytes.
        iin_field = application_iin.ToIIN()
        self._logger.log(
            f"Outstation.GetApplicationIIN: IINField LSB={iin_field.LSB}, MSB={iin_field.MSB}"
        )
        return application_iin

    def SupportsAssignClass(self) -> bool:
        """
        Assing class unsoported.
        Overridden method.
        """
        self._logger.log("In Outstation.SupportsAssignClass")
        return False

    def SupportsWriteAbsoluteTime(self) -> bool:
        """
        Write absolute time unsupported.
        Overridden method.
        """
        self._logger.log("In Outstation.SupportsWriteAbsoluteTime")
        return False

    def SupportsWriteTimeAndInterval(self) -> bool:
        """
        Write Time And Interval unsopported.
        Overridden method.
        """
        self._logger.log("In Outstation.SupportsWriteTimeAndInterval")
        return False

    def WarmRestartSupport(self) -> opendnp3.RestartMode:
        """
        Return a RestartMode enumerated value indicating whether a warm restart is supported.
        Warm restart unsoported.
        Overridden method.
        """
        self._logger.log("In Outstation.WarmRestartSupport")
        return opendnp3.RestartMode.UNSUPPORTED

    def ColdRestartSupport(self) -> opendnp3.RestartMode:
        """
        Return a RestartMode enumerated value indicating whether cold restart is supported.
        Cold restart unsoported.
        Overridden method.
        """
        self._logger.log("In Outstation.ColdRestartSupport")
        return opendnp3.RestartMode.UNSUPPORTED
