import HyWorksApiGRPC as HyWorksApi


class HypersimDataReader:
    def __init__(self):
        HyWorksApi.startAndConnectHypersim()
        self._sensors: set[str] = set()

    def add_sensor(self, sensor: str) -> None:
        if sensor in self._sensors:
            print(f"Sensor {sensor} already added.")
        self._sensors.add(sensor)

    def read(self) -> dict[str, float]:
        # TODO: Add somekind of retry here to fetch data again in case of error
        values = HyWorksApi.getLastSensorValues(list(self._sensors))
        if len(values) != len(self._sensors):
            raise ValueError(
                "An error occurred while reading sensors. The number of read values does not match the number of sensors."
            )
        return {key: value for key, value in zip(self._sensors, values)}
