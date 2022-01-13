from typing import Dict, Union
from utils import Logger
from proc.ied import Ied, DNP3Ied


def create_ied(ied: Dict) -> Union[Ied, None]:
    """
    Create an ied server.

    Args:
        ied (Dict):
            {
                "protocol": [dnp3 | iec61850],
                "port":     [int],
                "ns":       [str] (optional)
            }
        return (Union[Ied, None]): Return the new Ied o success, None on fail.
    """

    logger = Logger("Ied")

    if not 'protocol' in ied:
        logger.error(f"'protocol' is required on ied: {ied}")
        return None

    if not 'port' in ied:
        logger.error(f"'port' is required on ied: {ied}")
        return None

    if 'ns' not in ied:
        ied['ns'] = None

    if ied['protocol'] == 'dnp3':
        IedClass = DNP3Ied
    else:
        logger.error(f"Bad ied protocol '{ied['protocol']} in {ied}'")

    new_ied = IedClass(ied['port'], ied['ns'])
    new_ied.start()

    return new_ied
