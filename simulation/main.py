import argparse
import json
from datetime import datetime, timezone
from typing import Protocol, TypedDict

import HyWorksApiGRPC as HyWorksApi
from splight_lib.execution import ExecutionEngine, Task
from splight_lib.models import Asset
from splight_lib.models._v3.native import Number
from splight_lib.settings import (
    api_settings,
    datalake_settings,
    workspace_settings,
)


class AssetSummary(TypedDict):
    id: str
    kind: str


class DataReader(Protocol):
    def read(self) -> list[float]:
        pass


class DataSaver(Protocol):
    def save(self, data: list[float]) -> None:
        pass


class HypersimDataReader:
    def __init__(self):
        HyWorksApi.startAndConnectHypersim()
        self._sensors: set[str] = set()

    def add_sensor(self, sensor: str) -> None:
        if sensor in self._sensors:
            print(f"Sensor {sensor} already added.")
        self._sensors.add(sensor)

    def read(self) -> dict[str, float]:
        values = HyWorksApi.getLastSensorValues(list(self._sensors))
        if len(values) != len(self._sensors):
            raise ValueError(
                "An error occurred while reading sensors. The number of read values does not match the number of sensors."
            )
        return {key: value for key, value in zip(self._sensors, values)}


class DeviceDataSaver:
    def __init__(self, asset: Asset):
        self._asset = asset
        self._attributes = {item.name: item for item in asset.attributes}
        self._attr_sensor_map: dict[str, str] = {}

    def add_attribute(self, attribute: str, sensor: str) -> None:
        if attribute not in self._attributes:
            raise ValueError(f"Attribute {attribute} not found in asset.")
        if attribute in self._attr_sensor_map:
            print(f"Attribute {attribute} already added.")
        self._attr_sensor_map[sensor] = self._attributes[attribute]

    def process_data(
        self, data: dict[str, float], date: datetime
    ) -> dict[str, float]:
        for sensor, attribute in self._attr_sensor_map.items():
            sensor_value = data.get(sensor, None)
            if sensor_value is None:
                print(f"Sensor {sensor} not found in data.")
                return
            print(
                f"Saving data for sensor {sensor} with value {sensor_value}"
            )
            attr_value = Number(
                timestamp=date,
                asset=self._asset.id,
                attribute=attribute.id,
                value=sensor_value,
            )
            attr_value.save()


class HypersimConnector:
    def __init__(self, reader: DataReader):
        self._reader = reader
        self._data_savers: list[DataSaver] = []

    def add_data_saver(
        self,
        saver: DataSaver,
    ) -> None:
        self._data_savers.append(saver)

    def process(self) -> None:
        print("Reading data")
        now = datetime.now(timezone.utc)
        data = self._reader.read()
        for saver in self._data_savers:
            saver.process_data(data, now)


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
    args = parser.parse_args()
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
    connector_task = Task(
        target=connector.process,
        period=60,
    )

    connector.process()

    engine = ExecutionEngine()
    engine.add_task(connector_task, in_background=False, exit_on_fail=True)
    engine.start()


if __name__ == "__main__":
    main()
