from datetime import datetime, timezone

from hypersim.interfaces import DataReader, DataSaver


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
