from typing import Dict, Union

from proc.ied import C37118Ied, DNP3Ied, Ied
from utils import Logger


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

    if 'protocol' not in ied:
        logger.error(f"'protocol' is required on ied: {ied}")
        return None

    if 'port' not in ied:
        logger.error(f"'port' is required on ied: {ied}")
        return None

    if 'ns' not in ied:
        ied['ns'] = None

    if ied['protocol'] == 'dnp3':
        IedClass = DNP3Ied
    elif ied['protocol'] == 'c37118':
        IedClass = C37118Ied
    else:
        logger.error(f"Bad ied protocol '{ied['protocol']} in {ied}'")

    new_ied = IedClass(ied['port'], ied['ns'])
    new_ied.start()

    return new_ied
