import logging
import os
import sys

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(os.getenv("LOG_LEVEL", logging.INFO))
logger.addHandler(handler)

logger.debug("Logger initialized")
