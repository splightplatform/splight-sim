#!/bin/python3

import sys
import signal
from parser import parse_file, create
from utils import Logger
from utils.constants import USAGE, HEADER


def clean_exit(exit_code: int = 0) -> None:
    """
    Clean all before exit.

    Args:
        exit_code (int): Main process exit code.
    """

    #  for ied in ieds:
        #  del ied
#
    #  for vpn in vpns:
        #  del vpn

    sys.exit(exit_code)


def wait_exit(ieds, vpns) -> None:
    """Wait for all instances to finish."""

    for ied in ieds:
        ied.wait()

    for vpn in vpns:
        vpn.wait()

    sys.exit(0)


def usage(exit_code: int = 1, msg: str = None):
    """Print usage and exit."""

    if msg is not None:
        print(f"[ ERROR ] {msg}")

    print(USAGE)
    clean_exit(exit_code)


def exit_handler(sig, frame):
    print("")
    clean_exit()


def main():
    """ Main """
    logger = Logger("Main")
    logger.title(HEADER)

    signal.signal(signal.SIGINT, exit_handler)

    args = parse_file("/root/data/network.json")

    ieds = create(args, 'vpns')
    vpns = create(args, 'ieds')

    logger.info("Waiting subprocess\n\tPress 'ctr + c' to exit")

    wait_exit(ieds, vpns)


if __name__ == "__main__":
    main()
