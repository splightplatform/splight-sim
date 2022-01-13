import threading
import signal
import sys

from node import Outstation
from utils.logger import Logger
from utils.types import Node, OUTSTATION_TYPE, MASTER_TYPE
from argparse import ArgumentParser


exit_event = threading.Event()


def exit_handler(_, __) -> None:
    """Handle a singal to exit."""
    exit_event.set()


def run_node(node_type: str) -> None:
    """The main function, entry point."""
    # Store the original signal handler
    original_sigint_handler = signal.getsignal(signal.SIGINT)
    # Disable SIGINT (ctrl + c) signal until initialization finish
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    logger = Logger("MAIN")

    # Parse arguments
    if len(sys.argv) != 2:
        logger.error("Bad arguments")
        sys.exit()
    else:
        port = int(sys.argv[1])

    node: Node
    # Precondition: node_type is valid
    logger.log("Creating Outstation")
    node = Outstation(port=port)

    logger.log("Sleeping the main thread.")
    # Enable SIGINT and set handler
    signal.signal(signal.SIGINT, exit_handler)

    # Wait until SIGINT
    exit_event.wait()

    logger.log("Main thread wake up")
    # Restore signal handler
    signal.signal(signal.SIGINT, original_sigint_handler)

    logger.log("Shutdown Node")
    node.shutdown()

    # TODO: Close connections on com_handler.
    #       Require the implementation on the splight-lib.

    logger.log("Bye")
    sys.exit()
