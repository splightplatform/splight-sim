from datetime import datetime
from logging import getLogger

from splight_lib.models import Asset

# TODO: Update to use v3 models
from splight_lib.models._v3.native import Number

logger = getLogger("HypersimOperator")


class DeviceDataSaver:
    def __init__(self, asset: Asset):
        self._asset = asset
        self._attributes = {item.name: item for item in asset.attributes}
        self._attr_sensor_map: dict[str, str] = {}

    def add_attribute(self, attribute: str, sensor: str) -> None:
        if attribute not in self._attributes:
            raise ValueError(f"Attribute {attribute} not found in asset.")
        if attribute in self._attr_sensor_map:
            logger.debug(f"Attribute {attribute} already added.")
        self._attr_sensor_map[sensor] = self._attributes[attribute]

    def process_data(
        self, data: dict[str, float], date: datetime
    ) -> dict[str, float]:
        for sensor, attribute in self._attr_sensor_map.items():
            sensor_value = data.get(sensor, None)
            if sensor_value is None:
                logger.debug(f"Sensor {sensor} not found in data.")
                continue
            logger.debug(
                f"Saving data for sensor {sensor} with value {sensor_value}"
            )
            attr_value = Number(
                timestamp=date,
                asset=self._asset.id,
                attribute=attribute.id,
                value=sensor_value,
            )
            attr_value.save()
