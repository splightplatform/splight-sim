from datetime import datetime, timedelta, timezone
from time import sleep
from typing import TypedDict

import HyWorksApiGRPC as HyWorksApi
from splight_lib.models._v3.datalake import DataRequest, PipelineStep, Trace
from splight_lib.models._v3.native import Boolean, Number, String
from tenacity import retry, stop_after_attempt, wait_fixed

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
        self._connect()
        self._sensors: set[str] = set(sensors) if sensors else set()
        self._data: dict[str, float] = {}

    def add_sensor(self, sensor: str) -> None:
        if sensor in self._sensors:
            print(f"Sensor {sensor} already added.")
        self._sensors.add(sensor)

    def update_data(self) -> None:
        try:
            values = self._read_sensor_values()
        except Exception as e:
            print(f"Error reading sensors: {e}")
            self._connect()
            raise e
        # values = [0] * len(self._sensors)
        if len(values) != len(self._sensors):
            raise ValueError(
                (
                    "An error occurred while reading sensors. The number of "
                    "read values does not match the number of sensors."
                )
            )
        self._data = {key: value for key, value in zip(self._sensors, values)}

    def read(self) -> dict[str, float]:
        return self._data

    @retry(wait=wait_fixed(0.1), stop=stop_after_attempt(5))
    def _read_sensor_values(self) -> list[float]:
        values = HyWorksApi.getLastSensorValues(list(self._sensors))
        return values

    def _connect(self) -> None:
        HyWorksApi.startAndConnectHypersim()
        return None


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
