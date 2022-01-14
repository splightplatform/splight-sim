from proc.vpn import Vpn

class OvpnVpn(Vpn):
    """OpenVpn implementation."""

    def connect(self):
        """Connect to the OpenVpn VPN."""
        self._logger.log("Connecting")
        extra_auth_args = ""

        if self._user and self._pass:
            extra_auth_args = f"--auth-user-pass <(echo -e '{self._user}\\n{self._pass}')"

        cmd = "bash -c \"openvpn-ns " + \
              f"--namespace {self._ns} " + \
              f"--config {self._file} " + \
              f"{extra_auth_args}\""

        if super().run(cmd, 3) is not None:
            self._logger.error("Vpn connection error:" +
                               f"{self._popen.communicate()}")

        self._logger.success("Connection finish")
