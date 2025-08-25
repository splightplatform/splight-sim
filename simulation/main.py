import argparse
import json
import sys
from logging import Formatter, StreamHandler, getLogger
from threading import Event, Thread
from time import sleep
from typing import Dict, TypedDict

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


class HypersimDCMOrchestrator:
    def __init__(self, config: Dict):
        self._engine = ExecutionEngine()
        self._event = Event()

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
        self._reader_task = Thread(
            target=self._update_data_continuously, args=(reader,), daemon=True
        )
        self._operation_task = Thread(
            target=self._run_operation, args=(operator,), daemon=True
        )
        self._engine.add_task(
            connector_task,
            in_background=False,
            exit_on_fail=False,
            max_instances=2,
        )
        self._engine.add_task(
            update_task,
            in_background=False,
            exit_on_fail=False,
            max_instances=2,
        )

    def start(self) -> None:
        self._event.set()
        self._reader_task.start()
        self._operation_task.start()
        self._engine.start()

    def stop(self) -> None:
        self._event.clear()
        self._engine.stop()
        self._operation_task.join()
        self._reader_task.join()

    def _update_data_continuously(self, reader: HypersimDataReader) -> None:
        while self._event.is_set():
            try:
                reader.update_data()
            except Exception as e:
                logger.error(f"Error updating data: {e}")
            sleep(0.5)

    def _run_operation(self, operator: DCMHypersimOperator) -> None:
        while self._event.is_set():
            try:
                operator.run()
            except Exception as e:
                logger.error(f"Error running operation: {e}")
            sleep(0.01)


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

    orchestrator = HypersimDCMOrchestrator(config)

    try:
        orchestrator.start()
    except KeyboardInterrupt:
        orchestrator.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
