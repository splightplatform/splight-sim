import argparse
import json
from typing import TypedDict

from splight_lib.execution import ExecutionEngine, Task
from splight_lib.models import Asset


class AssetSummary(TypedDict):
    id: str
    kind: str


class HypersimDataReader:
    def __init__(self):
        self._sensors_map: dict[str, dict[str, str]] = {}

    def add_asset(
        self, asset: AssetSummary, attributes: dict[str, str]
    ) -> None:
        """Add an asset to the data reader."""
        instance = Asset.retrieve(asset["id"])
        asset_attributes = {attr.name: attr for attr in instance.attributes}

        for attr, sensor in attributes.items():
            self._sensors_map.update(
                {
                    sensor: {
                        "asset": asset["id"],
                        "attribute": asset_attributes[attr],
                    }
                }
            )

    def process(self) -> None:
        print("Reading data")


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
    for device, device_info in config["devices"].items():
        reader.add_asset(
            asset=device_info["asset"], attributes=device_info["attributes"]
        )
    reader_task = Task(
        target=reader.process,
        period=60,
    )

    engine = ExecutionEngine()
    engine.add_task(reader_task, in_background=False, exit_on_fail=True)
    engine.start()


if __name__ == "__main__":
    main()
