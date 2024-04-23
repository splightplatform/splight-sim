from pydnp3 import opendnp3
from utils.logger import Logger


class MasterApplication(opendnp3.IMasterApplication):
    def __init__(self):
        # Init the logger
        self._logger = Logger("MASTER_APP")
        # IMasterApplication __init__
        super().__init__()

    def AssignClassDuringStartup(self):
        """Overridden method"""
        self._logger.debug("Assign Class During Startup")
        return False

    def OnClose(self):
        """Overridden method"""
        self._logger.debug("Close")

    def OnOpen(self):
        """Overridden method"""
        self._logger.debug("Open")

    def OnReceiveIIN(self, iin):
        """Overridden method"""
        self._logger.debug(f"IIN received: {iin}")

    def OnTaskComplete(self, info):
        """Overridden method"""
        self._logger.debug(f"Task complete, info: {info}")

    def OnTaskStart(self, task_type, task_id):
        """Overridden method"""
        self._logger.debug(f"Task {task_id} of type {task_type} starts")
