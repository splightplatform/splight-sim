import argparse
import json
from typing import TypedDict

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
        __import__('ipdb').set_trace()


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
    for device in config["devices"].items():
        reader.add_asset(
            asset=device["asset"], attributes=device["attributes"]
        )

    __import__("ipdb").set_trace()


if __name__ == "__main__":
    main()
