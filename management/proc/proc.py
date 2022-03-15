import os
import subprocess
import time
from typing import Union


class Proc():
    """Simple abstract class for a process."""
    def __init__(self):
        self._popen = None

    def run(self, cmd: str, timeout: int) -> Union[int, None]:
        """
        Run in background.

        Args:
            cmd (str): Command to run.
            timeout (int): Time to wait before check the process and return.
            return (Union[int, None]): Return None on success or exit code on fail.
        """

        if False:
            self._popen = subprocess.Popen(cmd, shell=True)
        else:
            self._popen = subprocess.Popen(cmd, shell=True,
                                           stdin=subprocess.DEVNULL,
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL)

        # TODO: wait until "nitialization Sequence Completed\n" and alarm
        time.sleep(timeout)

        self._popen.poll()
        return self._popen.returncode

    def wait(self) -> None:
        """Wait to the process to finish."""
        if self._popen is not None:
            self._popen.wait()

    def kill(self) -> None:
        """Kill the process."""
        if self._popen is not None:
            self._popen.kill()
