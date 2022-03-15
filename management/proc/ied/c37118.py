
from proc.ied.ied import Ied


class C37118Ied(Ied):
    """c37.118 Ied simulator wrapper."""

    def start(self) -> None:
        """Start the simulation."""

        cmd = f"c37118 --port {self._port}"

        if self._ns is not None:
            cmd = f"ip netns exec {self._ns} {cmd}"

        cmd = f"sh -c '{cmd}'"

        if super().run(cmd, 1) is not None:
            self._logger.error(f"Ied run error: {self._popen.communicate()}")

        self._logger.success("Started")
