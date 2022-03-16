from proc.ied.ied import Ied


class IEC61850Ied(Ied):
    """IEC61850 Ied simulator wrapper."""

    def start(self) -> None:
        """Start the simulation."""

        cmd = f"iec61850 {self._port} /root/data/"

        if self._ns is not None:
            cmd = f"ip netns exec {self._ns} {cmd}"

        cmd = f"sh -c '{cmd}'"

        if super().run(cmd, 1) is not None:
            self._logger.error(f"Ied run error: {self._popen.communicate()}")

        self._logger.success("Started")
