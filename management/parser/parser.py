import sys
from parser.ied import create_ied
from parser.network import create_network
from utils import Logger

METHODS = {
    'vpns': create_network,
    'ieds': create_ied
}

def create(args: dict, key: str):
    """ Create instances """

    logger = Logger(f"Create {key}")
    logger.log("Creating instances")

    procs = []

    if key in args:
        var_list = args[key]
        if not isinstance(var_list, list):
            logger.error(f"Parsing input: '{key}' must be a list")
            sys.exit(1)

        for var in var_list:
            procs.append(METHODS[key](var))

    logger.log("Creation finish")
    return procs
