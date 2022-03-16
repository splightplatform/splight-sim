
from proc.ied.ied import Ied


class IEC60870Ied(Ied):
    """IEC60870-5-104 Ied simulator wrapper."""

    def start(self) -> None:
        """Start the simulation."""

        cmd = f"iec60870 {self._port}"

        if self._ns is not None:
            cmd = f"ip netns exec {self._ns} {cmd}"

        cmd = f"sh -c '{cmd}'"

        if super().run(cmd, 1) is not None:
            self._logger.error(f"Ied run error: {self._popen.communicate()}")

        self._logger.success("Started")
