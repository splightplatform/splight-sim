from typing import Protocol


class DataReader(Protocol):
    def read(self) -> list[float]:
        pass


class DataSaver(Protocol):
    def save(self, data: list[float]) -> None:
        pass
