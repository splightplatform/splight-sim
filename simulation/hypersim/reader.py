from datetime import datetime, timedelta, timezone
from typing import TypedDict

import HyWorksApiGRPC as HyWorksApi
from splight_lib.models._v3.datalake import DataRequest, PipelineStep, Trace
from splight_lib.models._v3.native import Boolean, Number, String

TYPE_MAP = {
    "number": Number,
    "string": String,
    "boolean": Boolean,
}


class DataAddress(TypedDict):
    asset: str
    attribute: str


class HypersimDataReader:
    def __init__(self, sensors: list[str] | None = None):
        # HyWorksApi.startAndConnectHypersim()
        self._sensors: set[str] = set(sensors) if sensors else set()

    def add_sensor(self, sensor: str) -> None:
        if sensor in self._sensors:
            print(f"Sensor {sensor} already added.")
        self._sensors.add(sensor)

    def read(self) -> dict[str, float]:
        # TODO: Add somekind of retry here to fetch data again in case of error
        values = HyWorksApi.getLastSensorValues(list(self._sensors))
        # values = [1.0] * len(self._sensors)
        if len(values) != len(self._sensors):
            raise ValueError(
                (
                    "An error occurred while reading sensors. The number of "
                    "read values does not match the number of sensors."
                )
            )
        return {key: value for key, value in zip(self._sensors, values)}


class AssetAttributeDataReader:
    def __init__(
        self,
        addresses: list[DataAddress],
        data_type: str = "Number",
        limit: int = 1000,
    ):
        self._addresses = addresses
        self._limit = limit
        self._data_class = TYPE_MAP.get(data_type.lower(), Number)

    def add_address(self, address: DataAddress) -> None:
        # TODO: validate if address already exists
        self._addresses.append(address)

    def read(self):
        now = datetime.now(timezone.utc)
        from_ts = now - timedelta(minutes=30)
        request = DataRequest[self._data_class](
            from_timestamp=from_ts,
            to_timestamp=now,
        )
        for address in self._addresses:
            trace = Trace.from_address(address["asset"], address["attribute"])
            trace.add_step(PipelineStep.from_dict({"$limit": self._limit}))
            request.add_trace(trace)
        data = request.apply()
        if len(data) != len(self._addresses):
            raise ValueError(
                (
                    "An error occurred while reading attributes. "
                    "The number of read values does not match the "
                    "number of addresses."
                )
            )
        return {item.asset: item.value for item in data}
