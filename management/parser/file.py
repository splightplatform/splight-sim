import json
import os
import sys
from typing import Dict, Union

from utils import Logger


def parse_file(filename: str) -> Union[Dict, None]:
    """
    Convert json file to dict.

    Args:
        filename (str): Path of the file.
        return (Union[Dict, None]): Return the parsed dict if success and None if fails.
    """

    logger = Logger("Parser")

    if not os.path.isfile(filename):
        logger.error("File not exists")
        sys.exit(1)

    try:
        with open(filename, "r", encoding="ascii") as json_file:
            return json.load(json_file)

    except ValueError as error:
        logger.error(f"Parsing json file: {error}")

    except Exception as error:
        logger.error(error)

    return None
