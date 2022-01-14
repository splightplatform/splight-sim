from utils import Logger
from proc.vpn import OvpnVpn, Vpn
from typing import Union, Dict
import os

def create_network(net: Dict) -> Union[Vpn, None]:
    """
    Create a vpn connection in a namespace.
    
    Args:
        net (Dict):
            {
                "file": [str],
                "ns":   [str],
                "user": [str] (optional),
                "pass": [str] (optional)
            }

        return (Union[Vpn, None]): Return the Vpn on success, None on fail.
    """

    logger = Logger("Network")

    if not 'file' in net:
        logger.error(f"Not 'file' in: {net}")
        return None

    if not 'ns' in net:
        logger.error(f"Not 'ns' in: {net}")
        return None

    net['file'] = "/root/data/" + net['file']
    if not os.path.isfile(net['file']):
        logger.error(f"Vpn file not exists in {net}")
        return None

    def set_def(obj: dict, key: str):
        if key not in obj:
            obj[key] = None

    set_def(net, 'user')
    set_def(net, 'pass')

    # By now only Openvpn
    VpnClass = OvpnVpn

    new_vpn = VpnClass(**net)
    new_vpn.connect()
    return new_vpn
