import argparse
import json
import sys
from time import sleep
from logging import Formatter, StreamHandler, getLogger
from threading import Event, Thread
from typing import TypedDict

from splight_lib.execution import ExecutionEngine, Task
from splight_lib.models import Asset
from splight_lib.settings import (
    api_settings,
    datalake_settings,
    workspace_settings,
)

from hypersim.data_connector import HypersimConnector
from hypersim.data_saver import DeviceDataSaver
from hypersim.operator import DCMHypersimOperator
from hypersim.reader import HypersimDataReader

logger = getLogger("HypersimOperator")
handler = StreamHandler()
formatter = Formatter(
    "%(levelname)s | %(asctime)s | %(filename)s:%(lineno)d | %(message)s"
)
handler.setFormatter(formatter)
event = Event()


class AssetSummary(TypedDict):
    id: str
    kind: str


def configure(file_path: dict) -> None:
    """Configures the splight lib"""
    with open(file_path, "r", encoding="utf-8") as file:
        config = json.load(file)
    workspace_settings.SPLIGHT_ACCESS_ID = config["splight_access_id"]
    workspace_settings.SPLIGHT_SECRET_KEY = config["splight_secret_key"]
    workspace_settings.SPLIGHT_PLATFORM_API_HOST = config.get(
        "splight_platform_api_host"
    )
    api_settings.API_VERSION = "v4"
    datalake_settings.DL_BUFFER_TIMEOUT = 10
    logger.debug("Configuring splight lib with provided credentials.")


def update_data_continuously(reader: HypersimDataReader) -> None:
    while event.is_set():
        try:
            reader.update_data()
        except Exception as e:
            logger.error(f"Error updating data: {e}")
        sleep(0.5)


def run_operation(operator: DCMHypersimOperator) -> None:
    while event.is_set():
        try:
            operator.run()
        except Exception as e:
            logger.error(f"Error running operation: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Run Hypersim simulation with config"
    )
    parser.add_argument(
        "--config-file",
        "-c",
        help="Path to JSON configuration file",
    )
    parser.add_argument(
        "--credentials-file",
        "-cf",
        help="Path to JSON credentials file",
    )
    parser.add_argument(
        "--log-level",
        "-l",
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        default="INFO",
    )
    args = parser.parse_args()

    # Set the level for this specific logger
    logger.setLevel(args.log_level.upper())
    # Add a handler to the logger (e.g., StreamHandler to print to console)
    logger.addHandler(handler)

    configure(args.credentials_file)
    with open(args.config_file, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    reader = HypersimDataReader()
    connector = HypersimConnector(reader)
    for device, device_info in config["devices"].items():
        asset = Asset.retrieve(device_info["asset"]["id"])
        saver = DeviceDataSaver(asset)
        for attr_name, sensor in device_info["attributes"].items():
            reader.add_sensor(sensor)
            saver.add_attribute(attr_name, sensor)
        connector.add_data_saver(saver)

    for line_info in config["monitored_lines"]:
        breaker = line_info["breaker"]
        reader.add_sensor(breaker)

    reader_task = Task(target=reader.update_data, period=1)

    connector_task = Task(
        target=connector.process,
        period=60,
    )
    operator = DCMHypersimOperator(
        config["grid"],
        config["monitored_lines"],
        config["generators"],
        reader,
    )
    update_task = Task(
        target=operator.update_operation_vectors,
        period=300,
    )
    # operation_task = Task(target=operator.run, period=1)
    reader_task = Thread(
        target=update_data_continuously, args=(reader,), daemon=True
    )
    operation_task = Thread(
        target=run_operation, args=(operator,), daemon=True
    )
    event.set()
    reader_task.start()
    operation_task.start()

    engine = ExecutionEngine()
    # engine.add_task(
    #     reader_task, in_background=True, exit_on_fail=True, max_instances=2
    # )
    engine.add_task(
        connector_task,
        in_background=False,
        exit_on_fail=False,
        max_instances=2,
    )
    engine.add_task(
        update_task, in_background=False, exit_on_fail=False, max_instances=2
    )
    # engine.add_task(operation_task, in_background=False, exit_on_fail=True)
    engine.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        event.clear()
        sys.exit(1)
