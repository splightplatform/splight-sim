from pydnp3 import openpal
from utils.logger import Logger


class ApplicationLogger(openpal.ILogHandler):
    """
    Override ILogHandler in this manner to implement application-specific logging behavior.
    """

    def __init__(self):
        super().__init__()
        self._logger = Logger("LOGGER")

    def Log(self, entry: openpal.LogEntry):
        """Overridden method"""
        filters = entry.filters.GetBitfield()
        location = entry.location.rsplit("/")[-1] if entry.location else ""
        message = entry.message
        self._logger.debug(
            f"filters: {filters} | location: {location} | entry: {message}"
        )
