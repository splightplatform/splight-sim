from pydnp3 import opendnp3, asiodnp3
from utils.logger import Logger


class ChannelListener(asiodnp3.IChannelListener):
    """
    Override IChannelListener in this manner to implement application-specific channel behavior.
    IChannelListener comes with the libreary, is the class in charge of the connections (TCP/IP).
    This will handle state changes in the connctions.
    """

    def __init__(self):
        super().__init__()
        self._logger = Logger("CHANNEL")

    def OnStateChange(self, state: opendnp3.ChannelState):
        """
        Overwrite of the IChannelListener class
        """
        self._logger.log(f"State change: {state}")
