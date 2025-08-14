import argparse
import json
from datetime import datetime, timezone
from typing import Protocol, TypedDict

from splight_lib.execution import ExecutionEngine, Task
from splight_lib.models import Asset, Number
import HyWorksApiGRPC as HyWorksApi


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
        return {key: value for key, value in zip(self._sensors, values)}


class DeviceDataSaver:
    def __init__(self, asset: Asset):
        self._asset = asset
        self._attributes = {item.name: item for item in asset.attributes}
        self._attr_sensor_map: dict[str, str] = {}

    def add_attribute(self, attribute: str, sensor: str) -> None:
        if attribute not in self._attributes:
            raise ValueError(f"Attribute {attribute} not found in asset.")
        if attribute in self._att_sensor_map:
            print(f"Attribute {attribute} already added.")
        self._attr_sensor_map[sensor] = self._attributes[attribute]

    def process_data(
        self, data: dict[str, float], date: datetime
    ) -> dict[str, float]:
        for sensor, attribute in self._attr_sensor_map.items():
            sensor_value = data.get(sensor, None)
            if sensor_value is None:
                print(f"Sensor {sensor} not found in data.")
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


def main():
    parser = argparse.ArgumentParser(
        description="Run Hypersim simulation with config"
    )
    parser.add_argument(
        "--config-file",
        "-c",
        help="Path to JSON configuration file",
    )
    args = parser.parse_args()
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
